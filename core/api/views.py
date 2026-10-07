"""
Vistas de la API REST de Mining Star.

Cada conjunto de vistas (ViewSet) expone un modulo del sistema con sus
cuatro operaciones. La autenticacion se resuelve con tokens JWT: el cliente
inicia sesion una vez, recibe un token y lo envia en la cabecera
Authorization de las peticiones siguientes.

Se eligio JWT y no la sesion de Django porque la API esta pensada para ser
consumida tambien desde un front-end independiente y desde una aplicacion
movil, donde no existe una cookie de sesion.
"""

from datetime import timedelta

from django.conf import settings
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group, User
from django.db.models import F, ProtectedError
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.types import OpenApiTypes
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .. import pagos, respaldos
from ..models import (
    AccionMejora,
    Cliente,
    Empleado,
    Interaccion,
    Oportunidad,
    Pedido,
    Producto,
    Proveedor,
    RegistroAcceso,
    RegistroProduccion,
    RequisitoNormativo,
    Venta,
)
from ..permisos import EDITAR, MATRIZ_DE_ACCESO, MODULOS, ROLES, VER, PermisoPorModulo
from ..servicios import (
    PedidoInvalido,
    StockInsuficiente,
    anular_venta,
    confirmar_pago,
    crear_pedido,
    eliminar_venta,
    registrar_venta,
    stock_materia_prima,
    total_vendido,
)
from .serializers import (
    AccionMejoraSerializer,
    CambiarRolSerializer,
    ClienteSerializer,
    CrearPedidoSerializer,
    EmpleadoSerializer,
    InteraccionSerializer,
    LoginSerializer,
    OportunidadSerializer,
    PedidoSerializer,
    ProduccionSerializer,
    ProductoSerializer,
    ProveedorSerializer,
    RegistrarVentaSerializer,
    RegistroAccesoSerializer,
    RegistroSerializer,
    RequisitoNormativoSerializer,
    ResumenSerializer,
    StockMateriaPrimaSerializer,
    UsuarioSerializer,
    VentaSerializer,
)


def _ip(request):
    # Se usa REMOTE_ADDR y no X-Forwarded-For: esa cabecera la escribe el
    # cliente y se puede falsificar para evadir el bloqueo por IP.
    return request.META.get("REMOTE_ADDR")


def _registrar_acceso(request, nombre, evento, usuario=None, jti=""):
    RegistroAcceso.objects.create(
        usuario=usuario,
        nombre_usuario=(nombre or "")[:150],
        evento=evento,
        ip=_ip(request),
        navegador=request.META.get("HTTP_USER_AGENT", "")[:255],
        token_jti=jti,
    )


def _ingreso_bloqueado(request, nombre):
    """True si el usuario o la IP superaron los intentos fallidos permitidos.

    Solo cuentan los fallos posteriores al ultimo ingreso exitoso: quien
    se equivoca dos veces y luego entra no arrastra esos fallos.
    """
    desde = timezone.now() - timedelta(minutes=settings.LOGIN_VENTANA_MINUTOS)
    ultimo_ok = (
        RegistroAcceso.objects.filter(nombre_usuario=nombre, evento="ingreso", fecha__gte=desde)
        .values_list("fecha", flat=True).first()
    )
    fallos_usuario = RegistroAcceso.objects.filter(
        nombre_usuario=nombre, evento="fallido", fecha__gte=ultimo_ok or desde
    ).count()
    fallos_ip = RegistroAcceso.objects.filter(
        ip=_ip(request), evento="fallido", fecha__gte=desde
    ).count()
    return (
        fallos_usuario >= settings.LOGIN_INTENTOS_MAXIMOS
        or fallos_ip >= settings.LOGIN_INTENTOS_MAXIMOS_POR_IP
    )

# ==========================================================
# AUTENTICACION — evidencia GA7-220501096-AA5-EV01
# ==========================================================

@extend_schema(
    tags=["Autenticacion"],
    summary="Registrar un usuario nuevo (solo Administrador)",
    description=(
        "Crea la cuenta de un empleado con su cargo. Solo un Administrador "
        "puede hacerlo: en un sistema empresarial nadie debe poder darse de "
        "alta a si mismo. Valida que el nombre de usuario y el correo no "
        "esten en uso, que las contrasenas coincidan y que la contrasena "
        "cumpla las reglas de seguridad de Django."
    ),
    responses={201: UsuarioSerializer},
)
class RegistroView(APIView):
    """Servicio de registro de usuarios.

    Antes era publico: cualquiera podia crear una cuenta y, con ella, leer
    los datos personales de clientes y empleados. Ahora exige el permiso
    "crear" del modulo de seguridad.
    """

    permission_classes = [PermisoPorModulo]
    modulo = "seguridad"
    serializer_class = RegistroSerializer

    def post(self, request):
        serializador = RegistroSerializer(data=request.data)
        if not serializador.is_valid():
            return Response(
                {"mensaje": "Error en el registro.", "errores": serializador.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario = serializador.save()
        return Response(
            {"mensaje": "Registro satisfactorio.", "usuario": UsuarioSerializer(usuario).data},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(
    tags=["Autenticacion"],
    summary="Iniciar sesion",
    description=(
        "Recibe un usuario y una contrasena. Si la autenticacion es correcta "
        "devuelve un mensaje de autenticacion satisfactoria junto a los tokens "
        "de acceso; en caso contrario devuelve error en la autenticacion."
    ),
    request=LoginSerializer,
    examples=[
        OpenApiExample(
            "Credenciales correctas",
            value={"username": "juan.ortega", "password": "********"},
            request_only=True,
        )
    ],
    auth=[],
)
class LoginView(APIView):
    """Servicio de inicio de sesion.

    Devuelve deliberadamente el mismo mensaje tanto si el usuario no existe
    como si la contrasena es incorrecta: distinguir ambos casos permitiria
    averiguar que nombres de usuario estan registrados.
    """

    permission_classes = [AllowAny]
    serializer_class = LoginSerializer

    def post(self, request):
        serializador = LoginSerializer(data=request.data)
        if not serializador.is_valid():
            return Response(
                {
                    "autenticado": False,
                    "mensaje": "Error en la autenticacion: faltan credenciales.",
                    "errores": serializador.errors,
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        nombre = serializador.validated_data["username"]
        if _ingreso_bloqueado(request, nombre):
            _registrar_acceso(request, nombre, "bloqueado")
            return Response(
                {
                    "autenticado": False,
                    "mensaje": (
                        "Demasiados intentos fallidos. Espere "
                        f"{settings.LOGIN_VENTANA_MINUTOS} minutos e intente de nuevo."
                    ),
                },
                status=status.HTTP_429_TOO_MANY_REQUESTS,
            )

        usuario = authenticate(
            username=nombre,
            password=serializador.validated_data["password"],
        )

        if usuario is None:
            _registrar_acceso(request, nombre, "fallido")
            return Response(
                {
                    "autenticado": False,
                    "mensaje": "Error en la autenticacion: usuario o contrasena incorrectos.",
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not usuario.is_active:
            return Response(
                {"autenticado": False, "mensaje": "Error en la autenticacion: cuenta inactiva."},
                status=status.HTTP_403_FORBIDDEN,
            )

        # Un token de acceso nuevo por cada ingreso. Se registra su
        # identificador (jti) para poder rastrear que hizo cada sesion.
        refresh = RefreshToken.for_user(usuario)
        acceso = refresh.access_token
        _registrar_acceso(request, nombre, "ingreso", usuario, jti=acceso["jti"])
        usuario.last_login = timezone.now()
        usuario.save(update_fields=["last_login"])
        return Response(
            {
                "autenticado": True,
                "mensaje": "Autenticacion satisfactoria.",
                "usuario": UsuarioSerializer(usuario).data,
                "access": str(acceso),
                "refresh": str(refresh),
                "expira_en_minutos": int(
                    settings.SIMPLE_JWT["ACCESS_TOKEN_LIFETIME"].total_seconds() // 60
                ),
            },
            status=status.HTTP_200_OK,
        )


@extend_schema(
    tags=["Autenticacion"],
    summary="Cerrar sesion e invalidar el token de refresco",
    request={"application/json": {"type": "object", "properties": {"refresh": {"type": "string"}}}},
    responses=OpenApiTypes.OBJECT,
)
class LogoutView(APIView):
    """Pone el token de refresco en la lista negra: aunque alguien lo haya
    copiado, ya no sirve para obtener tokens de acceso nuevos."""

    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            RefreshToken(request.data.get("refresh", "")).blacklist()
        except TokenError:
            pass  # token vencido o ya invalidado: el resultado es el mismo
        _registrar_acceso(request, request.user.username, "salida", request.user)
        return Response({"mensaje": "Sesion cerrada."})


@extend_schema(
    tags=["Autenticacion"],
    summary="Consultar el perfil del usuario autenticado",
    responses={200: UsuarioSerializer},
)
class PerfilView(APIView):
    """Comprueba que el token recibido es valido y devuelve a quien pertenece."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UsuarioSerializer(request.user).data)


@extend_schema(
    tags=["Autenticacion"],
    summary="Renovar el token de acceso",
    description=(
        "Recibe el token de refresco y devuelve un token de acceso nuevo, "
        "para no pedir usuario y contrasena cada dos horas."
    ),
    auth=[],
)
class RefrescarTokenView(TokenRefreshView):
    pass


@extend_schema(
    tags=["Autenticacion"],
    summary="Verificar si un token sigue siendo valido",
    auth=[],
)
class VerificarTokenView(TokenVerifyView):
    pass


# ==========================================================
# MODULOS DEL PROYECTO — evidencia GA7-220501096-AA5-EV03
# ==========================================================

class BaseViewSet(viewsets.ModelViewSet):
    """Comportamiento comun a todos los modulos.

    Toda la API exige autenticacion: los datos de clientes y empleados son
    datos personales sujetos a la Ley 1581 de 2012 y no pueden quedar
    expuestos sin control de acceso.
    """

    permission_classes = [PermisoPorModulo]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]

    def destroy(self, request, *args, **kwargs):
        """Borra el registro, salvo que otros dependan de el.

        Los modelos usan on_delete=PROTECT: no se puede borrar un cliente con
        ventas, un proveedor con productos ni un producto ya vendido, porque
        se perderia el historico. Sin este control, Django lanza
        ProtectedError y la API responde con un error 500.
        """
        objeto = self.get_object()
        try:
            objeto.delete()
        except ProtectedError as error:
            dependientes = sorted({str(o._meta.verbose_name_plural) for o in error.protected_objects})
            return Response(
                {
                    "mensaje": (
                        f"No se puede eliminar {objeto}: tiene registros asociados en "
                        f"{', '.join(dependientes)}."
                    ),
                    "dependientes": dependientes,
                },
                status=status.HTTP_409_CONFLICT,
            )
        return Response(status=status.HTTP_204_NO_CONTENT)


@extend_schema(tags=["Clientes"])
class ClienteViewSet(BaseViewSet):
    modulo = "clientes"
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    search_fields = ["documento", "nombre", "empresa", "correo"]
    ordering_fields = ["nombre", "documento", "empresa"]


@extend_schema(tags=["Proveedores"])
class ProveedorViewSet(BaseViewSet):
    modulo = "proveedores"
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    search_fields = ["nit", "empresa", "contacto", "ciudad"]
    ordering_fields = ["empresa", "ciudad"]


@extend_schema(tags=["Productos"])
class ProductoViewSet(BaseViewSet):
    modulo = "productos"
    queryset = Producto.objects.select_related("proveedor")
    serializer_class = ProductoSerializer
    filterset_fields = ["categoria", "proveedor"]
    search_fields = ["codigo", "nombre", "categoria"]
    ordering_fields = ["nombre", "precio_venta", "stock"]

    @extend_schema(
        summary="Listar los productos que llegaron al minimo de inventario",
        responses={200: ProductoSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="stock-bajo")
    def stock_bajo(self, request):
        """Servicio de apoyo a la reposicion de inventario."""
        consulta = self.get_queryset().filter(stock__lte=F("stock_minimo"))
        return Response(self.get_serializer(consulta, many=True).data)


@extend_schema(tags=["Empleados"])
class EmpleadoViewSet(BaseViewSet):
    modulo = "empleados"
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    filterset_fields = ["cargo", "area", "estado"]
    search_fields = ["documento", "nombres", "apellidos", "correo"]
    ordering_fields = ["nombres", "apellidos", "fecha_ingreso"]


@extend_schema(tags=["Produccion"])
class ProduccionViewSet(BaseViewSet):
    """Produccion diaria de la mina (historia de usuario HU-001)."""

    modulo = "produccion"

    queryset = RegistroProduccion.objects.select_related("supervisor", "registrado_por")
    serializer_class = ProduccionSerializer
    filterset_fields = ["fecha", "turno", "material"]
    search_fields = ["observaciones"]
    ordering_fields = ["fecha", "cantidad"]

    def perform_create(self, serializer):
        serializer.save(registrado_por=self.request.user)

    @extend_schema(
        summary="Stock de materia prima en la mina",
        responses={200: StockMateriaPrimaSerializer(many=True)},
    )
    @action(detail=False, methods=["get"], url_path="stock-materia-prima")
    def stock_materia_prima(self, request):
        return Response(StockMateriaPrimaSerializer(stock_materia_prima(), many=True).data)


@extend_schema(tags=["Ventas"])
class VentaViewSet(
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet,
):
    """Modulo de ventas.

    A diferencia de los demas modulos, no hereda de ModelViewSet: una venta
    no se crea ni se edita con un POST o un PUT generico, porque eso la
    guardaria sin detalle y sin descontar inventario. Se exponen solo:

    - listar y consultar;
    - registrar (/registrar/) y anular (/{id}/anular/), que pasan por el
      servicio de dominio;
    - eliminar, que tambien pasa por el servicio para devolver el stock.
    """

    permission_classes = [PermisoPorModulo]
    modulo = "ventas"
    operaciones_por_accion = {"anular": EDITAR}
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    queryset = Venta.objects.select_related("cliente", "empleado").prefetch_related(
        "detalles__producto"
    )
    serializer_class = VentaSerializer
    filterset_fields = ["estado", "cliente"]
    ordering_fields = ["fecha", "total"]

    def perform_destroy(self, venta):
        # El borrado generico de DRF solo haria venta.delete() y las
        # unidades vendidas se perderian del inventario.
        eliminar_venta(venta)

    @extend_schema(
        summary="Registrar una venta descontando inventario",
        request=RegistrarVentaSerializer,
        responses={201: VentaSerializer},
    )
    @action(detail=False, methods=["post"])
    def registrar(self, request):
        serializador = RegistrarVentaSerializer(data=request.data)
        if not serializador.is_valid():
            return Response(
                {"mensaje": "Error en el registro de la venta.", "errores": serializador.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        datos = serializador.validated_data
        try:
            venta = registrar_venta(
                cliente=datos["cliente"],
                producto=datos["producto"],
                cantidad=datos["cantidad"],
                empleado=datos.get("empleado"),
            )
        except StockInsuficiente as error:
            # Se llega aqui cuando otro usuario vendio entre la validacion
            # y la escritura. El descuento condicional lo detecta y deshace
            # la transaccion completa.
            return Response(
                {
                    "mensaje": "Stock insuficiente: otro usuario acaba de vender ese producto.",
                    "producto": error.producto,
                },
                status=status.HTTP_409_CONFLICT,
            )

        return Response(
            {"mensaje": "Venta registrada correctamente.", "venta": VentaSerializer(venta).data},
            status=status.HTTP_201_CREATED,
        )

    @extend_schema(
        summary="Anular una venta y devolver el inventario",
        request=None,
        responses={200: VentaSerializer},
    )
    @action(detail=True, methods=["post"])
    def anular(self, request, pk=None):
        venta = self.get_object()
        if venta.estado == "Anulada":
            return Response(
                {"mensaje": "La venta ya estaba anulada."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        venta = anular_venta(venta)
        return Response(
            {"mensaje": "Venta anulada y stock devuelto al inventario.",
             "venta": VentaSerializer(venta).data}
        )


@extend_schema(
    tags=["Panel"],
    summary="Indicadores agregados del sistema",
    description="Totales de cada modulo para alimentar un panel de control.",
    responses={200: ResumenSerializer},
)
class ResumenView(APIView):
    """Servicio de apoyo: evita que el cliente pida cinco listados completos
    solo para mostrar cuatro numeros en pantalla."""

    permission_classes = [PermisoPorModulo]
    modulo = "panel"
    serializer_class = ResumenSerializer

    def get(self, request):
        datos = {
            "clientes": Cliente.objects.count(),
            "proveedores": Proveedor.objects.count(),
            "productos": Producto.objects.count(),
            "empleados": Empleado.objects.count(),
            "ventas": Venta.objects.exclude(estado="Anulada").count(),
            "total_vendido": total_vendido(),
            "productos_stock_bajo": Producto.objects.filter(
                stock__lte=F("stock_minimo")
            ).count(),
        }
        return Response(ResumenSerializer(datos).data)


# ==========================================================
# CRM
# ==========================================================

@extend_schema(tags=["CRM"])
class OportunidadViewSet(BaseViewSet):
    """Embudo comercial: oportunidades de negocio por etapa."""

    modulo = "crm"
    queryset = Oportunidad.objects.select_related("cliente", "responsable")
    serializer_class = OportunidadSerializer
    filterset_fields = ["etapa", "cliente", "responsable"]
    search_fields = ["titulo", "cliente__nombre", "notas"]
    ordering_fields = ["valor_estimado", "actualizado", "fecha_cierre_estimada"]


@extend_schema(tags=["CRM"])
class InteraccionViewSet(BaseViewSet):
    """Historial de contactos con cada cliente."""

    modulo = "crm"
    queryset = Interaccion.objects.select_related("cliente", "registrado_por")
    serializer_class = InteraccionSerializer
    filterset_fields = ["cliente", "tipo", "oportunidad"]
    search_fields = ["descripcion", "cliente__nombre"]
    ordering_fields = ["fecha"]

    def perform_create(self, serializer):
        serializer.save(registrado_por=self.request.user)


# ==========================================================
# TIENDA: CARRITO, PEDIDOS Y PAGOS
# ==========================================================

@extend_schema(tags=["Tienda y pagos"])
class PedidoViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    """Pedidos creados desde el carrito y su pago.

    Flujo: POST /pedidos/ (crea el pedido con el carrito) ->
    POST /pedidos/{id}/pagar/ (devuelve la URL de pago) ->
    el pago se confirma por el webhook de Stripe, por
    GET /pedidos/{id}/verificar/ al volver del pago, o por
    POST /pedidos/{id}/confirmar-simulado/ en modo demostracion.
    """

    permission_classes = [PermisoPorModulo]
    modulo = "pedidos"
    operaciones_por_accion = {"cancelar": EDITAR, "verificar": VER}
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    queryset = Pedido.objects.select_related("cliente").prefetch_related("items__producto")
    serializer_class = PedidoSerializer
    filterset_fields = ["estado", "cliente"]
    ordering_fields = ["creado", "total"]

    @extend_schema(request=CrearPedidoSerializer, responses={201: PedidoSerializer})
    def create(self, request):
        entrada = CrearPedidoSerializer(data=request.data)
        if not entrada.is_valid():
            return Response(
                {"mensaje": "El carrito tiene datos invalidos.", "errores": entrada.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )
        datos = entrada.validated_data
        try:
            pedido = crear_pedido(
                datos["cliente"],
                [(linea["producto"], linea["cantidad"]) for linea in datos["items"]],
                usuario=request.user,
            )
        except PedidoInvalido as error:
            return Response({"mensaje": str(error)}, status=status.HTTP_400_BAD_REQUEST)
        return Response(PedidoSerializer(pedido).data, status=status.HTTP_201_CREATED)

    @extend_schema(summary="Iniciar el pago del pedido", request=None)
    @action(detail=True, methods=["post"])
    def pagar(self, request, pk=None):
        pedido = self.get_object()
        if pedido.estado != "Pendiente":
            return Response(
                {"mensaje": f"El pedido esta {pedido.get_estado_display().lower()}."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if pagos.modo() == "simulado":
            return Response({"modo": "simulado", "url": None, "pedido": pedido.pk})

        base = settings.FRONTEND_URL
        referencia, url = pagos.crear_sesion(
            pedido,
            url_exito=f"{base}/tienda/resultado?pedido={pedido.pk}",
            url_cancelacion=f"{base}/tienda/carrito?cancelado={pedido.pk}",
        )
        pedido.referencia_pago = referencia
        pedido.metodo_pago = "stripe"
        pedido.save(update_fields=["referencia_pago", "metodo_pago"])
        return Response({"modo": "stripe", "url": url, "pedido": pedido.pk})

    @extend_schema(summary="Consultar en Stripe si el pedido ya se pago")
    @action(detail=True, methods=["get"])
    def verificar(self, request, pk=None):
        pedido = self.get_object()
        if pedido.estado == "Pendiente" and pedido.referencia_pago and pagos.modo() == "stripe":
            if pagos.sesion_pagada(pedido.referencia_pago):
                pedido = self._confirmar(pedido, "stripe", pedido.referencia_pago)
        return Response(PedidoSerializer(pedido).data)

    @extend_schema(summary="Aprobar el pago en modo demostracion", request=None)
    @action(detail=True, methods=["post"], url_path="confirmar-simulado")
    def confirmar_simulado(self, request, pk=None):
        if pagos.modo() != "simulado":
            return Response(
                {"mensaje": "Con Stripe configurado el pago solo se confirma desde la pasarela."},
                status=status.HTTP_403_FORBIDDEN,
            )
        pedido = self._confirmar(self.get_object(), "simulado", f"SIM-{timezone.now():%Y%m%d%H%M%S}")
        return Response(PedidoSerializer(pedido).data)

    @extend_schema(summary="Cancelar un pedido pendiente", request=None)
    @action(detail=True, methods=["post"])
    def cancelar(self, request, pk=None):
        pedido = self.get_object()
        if pedido.estado != "Pendiente":
            return Response({"mensaje": "Solo se cancelan pedidos pendientes."},
                            status=status.HTTP_400_BAD_REQUEST)
        pedido.estado = "Cancelado"
        pedido.save(update_fields=["estado"])
        return Response(PedidoSerializer(pedido).data)

    @staticmethod
    def _confirmar(pedido, metodo, referencia):
        try:
            return confirmar_pago(pedido, metodo, referencia)
        except StockInsuficiente:
            Pedido.objects.filter(pk=pedido.pk).update(estado="Fallido")
            pedido.refresh_from_db()
            return pedido


@extend_schema(tags=["Tienda y pagos"], summary="Modo de la pasarela de pagos", responses=OpenApiTypes.OBJECT)
class ConfigPagosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({"modo": pagos.modo(), "moneda": settings.STRIPE_MONEDA.upper()})


@extend_schema(exclude=True)
class StripeWebhookView(APIView):
    """Recibe los avisos de Stripe. Es publico, pero solo acepta mensajes con
    una firma valida hecha con STRIPE_WEBHOOK_SECRET."""

    permission_classes = [AllowAny]
    authentication_classes = []

    def post(self, request):
        if not settings.STRIPE_WEBHOOK_SECRET:
            return Response(status=status.HTTP_404_NOT_FOUND)
        try:
            evento = pagos.leer_evento_webhook(
                request.body, request.META.get("HTTP_STRIPE_SIGNATURE", "")
            )
        except Exception:  # firma invalida o cuerpo malformado
            return Response(status=status.HTTP_400_BAD_REQUEST)

        if evento["type"] == "checkout.session.completed":
            sesion = evento["data"]["object"]
            pedido = Pedido.objects.filter(pk=sesion.get("client_reference_id")).first()
            if pedido and sesion.get("payment_status") == "paid":
                PedidoViewSet._confirmar(pedido, "stripe", sesion["id"])
        return Response({"recibido": True})


# ==========================================================
# REQUISITOS MINEROS Y AMBIENTALES
# ==========================================================

@extend_schema(tags=["Normativa"])
class RequisitoNormativoViewSet(BaseViewSet):
    modulo = "normativa"
    queryset = RequisitoNormativo.objects.select_related("responsable")
    serializer_class = RequisitoNormativoSerializer
    filterset_fields = ["autoridad", "categoria", "estado"]
    search_fields = ["nombre", "norma", "descripcion"]
    ordering_fields = ["fecha_vencimiento", "nombre"]


# ==========================================================
# MEJORA CONTINUA
# ==========================================================

@extend_schema(tags=["Mejora continua"])
class AccionMejoraViewSet(BaseViewSet):
    modulo = "mejora"
    queryset = AccionMejora.objects.select_related("responsable", "creado_por")
    serializer_class = AccionMejoraSerializer
    filterset_fields = ["fase", "origen", "tipo"]
    search_fields = ["titulo", "descripcion"]
    ordering_fields = ["creado", "fecha_compromiso"]

    def perform_create(self, serializer):
        serializer.save(creado_por=self.request.user)


# ==========================================================
# SEGURIDAD: USUARIOS, ACCESOS, ROLES Y RESPALDOS
# ==========================================================

@extend_schema(tags=["Seguridad"])
class UsuarioViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, viewsets.GenericViewSet):
    permission_classes = [PermisoPorModulo]
    modulo = "seguridad"
    operaciones_por_accion = {"cambiar_rol": EDITAR, "activar": EDITAR}
    queryset = User.objects.prefetch_related("groups").select_related("empleado").order_by("username")
    serializer_class = UsuarioSerializer

    @extend_schema(request=CambiarRolSerializer)
    @action(detail=True, methods=["post"], url_path="cambiar-rol")
    def cambiar_rol(self, request, pk=None):
        usuario = self.get_object()
        entrada = CambiarRolSerializer(data=request.data)
        entrada.is_valid(raise_exception=True)
        if usuario == request.user:
            return Response({"mensaje": "No puede cambiar su propio cargo."},
                            status=status.HTTP_400_BAD_REQUEST)
        usuario.groups.remove(*Group.objects.filter(name__in=ROLES))
        usuario.groups.add(Group.objects.get_or_create(name=entrada.validated_data["rol"])[0])
        return Response(UsuarioSerializer(usuario).data)

    @extend_schema(request=None)
    @action(detail=True, methods=["post"])
    def activar(self, request, pk=None):
        """Activa o desactiva la cuenta. Desactivar es preferible a borrar:
        conserva el historial de lo que hizo el usuario."""
        usuario = self.get_object()
        if usuario == request.user:
            return Response({"mensaje": "No puede desactivar su propia cuenta."},
                            status=status.HTTP_400_BAD_REQUEST)
        usuario.is_active = not usuario.is_active
        usuario.save(update_fields=["is_active"])
        return Response(UsuarioSerializer(usuario).data)


@extend_schema(tags=["Seguridad"])
class RegistroAccesoViewSet(mixins.ListModelMixin, viewsets.GenericViewSet):
    """Bitacora de ingresos: quien entro, cuando, desde que IP y con que token."""

    permission_classes = [PermisoPorModulo]
    modulo = "seguridad"
    queryset = RegistroAcceso.objects.all()
    serializer_class = RegistroAccesoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ["evento"]
    search_fields = ["nombre_usuario", "ip"]


@extend_schema(tags=["Seguridad"], summary="Matriz de acceso por cargo", responses=OpenApiTypes.OBJECT)
class MatrizAccesoView(APIView):
    """Publica la matriz completa: cualquier empleado puede consultar que
    puede hacer cada cargo (transparencia), pero solo el Administrador
    asigna cargos."""

    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({
            "modulos": MODULOS,
            "roles": {
                rol: {modulo: sorted(ops) for modulo, ops in fila.items()}
                for rol, fila in MATRIZ_DE_ACCESO.items()
            },
        })


@extend_schema(tags=["Seguridad"], summary="Listar y crear copias de seguridad", request=None, responses=OpenApiTypes.OBJECT)
class RespaldoView(APIView):
    permission_classes = [PermisoPorModulo]
    modulo = "seguridad"

    def get(self, request):
        return Response(respaldos.listar_respaldos())

    def post(self, request):
        ruta = respaldos.crear_respaldo()
        return Response(
            {"mensaje": f"Respaldo creado: {ruta.name}", "respaldos": respaldos.listar_respaldos()},
            status=status.HTTP_201_CREATED,
        )


# ==========================================================
# DASHBOARD
# ==========================================================

@extend_schema(tags=["Panel"], summary="Datos para las graficas del dashboard", responses=OpenApiTypes.OBJECT)
class DashboardView(APIView):
    """Series agregadas para las graficas. Cada bloque solo se incluye si el
    cargo del usuario puede ver ese modulo: un operario no ve las ventas."""

    permission_classes = [PermisoPorModulo]
    modulo = "panel"

    def get(self, request):
        from ..permisos import puede
        from ..tablero import construir_dashboard

        visibles = {m for m in MODULOS if puede(request.user, m, VER)}
        return Response(construir_dashboard(visibles))
