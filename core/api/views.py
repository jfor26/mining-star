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

from django.contrib.auth import authenticate
from django.db.models import F
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import OpenApiExample, extend_schema
from rest_framework import filters, mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from ..models import Cliente, Empleado, Producto, Proveedor, Venta
from ..servicios import (
    StockInsuficiente,
    anular_venta,
    eliminar_venta,
    registrar_venta,
    total_vendido,
)
from .serializers import (
    ClienteSerializer,
    EmpleadoSerializer,
    LoginSerializer,
    ProductoSerializer,
    ProveedorSerializer,
    RegistrarVentaSerializer,
    RegistroSerializer,
    ResumenSerializer,
    UsuarioSerializer,
    VentaSerializer,
)

# ==========================================================
# AUTENTICACION — evidencia GA7-220501096-AA5-EV01
# ==========================================================

@extend_schema(
    tags=["Autenticacion"],
    summary="Registrar un usuario nuevo",
    description=(
        "Crea una cuenta de usuario. Valida que el nombre de usuario y el "
        "correo no esten en uso, que las dos contrasenas coincidan y que la "
        "contrasena cumpla las reglas de seguridad de Django."
    ),
    responses={201: UsuarioSerializer},
    auth=[],
)
class RegistroView(APIView):
    """Servicio de registro. Es el unico endpoint abierto junto al login."""

    permission_classes = [AllowAny]
    serializer_class = RegistroSerializer

    def post(self, request):
        serializador = RegistroSerializer(data=request.data)
        if not serializador.is_valid():
            return Response(
                {"mensaje": "Error en el registro.", "errores": serializador.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )

        usuario = serializador.save()
        refresh = RefreshToken.for_user(usuario)
        return Response(
            {
                "mensaje": "Registro satisfactorio.",
                "usuario": UsuarioSerializer(usuario).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
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

        usuario = authenticate(
            username=serializador.validated_data["username"],
            password=serializador.validated_data["password"],
        )

        if usuario is None:
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

        refresh = RefreshToken.for_user(usuario)
        return Response(
            {
                "autenticado": True,
                "mensaje": "Autenticacion satisfactoria.",
                "usuario": UsuarioSerializer(usuario).data,
                "access": str(refresh.access_token),
                "refresh": str(refresh),
            },
            status=status.HTTP_200_OK,
        )


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

    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]


@extend_schema(tags=["Clientes"])
class ClienteViewSet(BaseViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer
    search_fields = ["documento", "nombre", "empresa", "correo"]
    ordering_fields = ["nombre", "documento", "empresa"]


@extend_schema(tags=["Proveedores"])
class ProveedorViewSet(BaseViewSet):
    queryset = Proveedor.objects.all()
    serializer_class = ProveedorSerializer
    search_fields = ["nit", "empresa", "contacto", "ciudad"]
    ordering_fields = ["empresa", "ciudad"]


@extend_schema(tags=["Productos"])
class ProductoViewSet(BaseViewSet):
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
    queryset = Empleado.objects.all()
    serializer_class = EmpleadoSerializer
    filterset_fields = ["cargo", "area", "estado"]
    search_fields = ["documento", "nombres", "apellidos", "correo"]
    ordering_fields = ["nombres", "apellidos", "fecha_ingreso"]


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

    permission_classes = [IsAuthenticated]
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

    permission_classes = [IsAuthenticated]
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
