"""
Serializadores de la API REST de Mining Star.

Un serializador cumple en la API el mismo papel que un ModelForm en la capa
web: traduce entre los objetos de Python y el JSON que viaja por la red, y
—sobre todo— valida la entrada ANTES de que toque la base de datos.

Las reglas de validacion se derivan del modelo siempre que es posible, para
que no existan dos definiciones del mismo limite que puedan divergir.
"""

from django.contrib.auth.models import Group, User
from django.contrib.auth.password_validation import validate_password
from django.utils import timezone
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from ..models import (
    AccionMejora,
    Cliente,
    DetalleVenta,
    Empleado,
    Interaccion,
    ItemPedido,
    Oportunidad,
    Pedido,
    Producto,
    Proveedor,
    RegistroAcceso,
    RegistroProduccion,
    RequisitoNormativo,
    Venta,
)
from ..permisos import ROLES, permisos_de, rol_de

# ==========================================================
# AUTENTICACION
# ==========================================================

class RegistroSerializer(serializers.ModelSerializer):
    """Valida el alta de un usuario nuevo.

    La contrasena se recibe dos veces y nunca se devuelve: write_only impide
    que aparezca en ninguna respuesta de la API.
    """

    password = serializers.CharField(
        write_only=True,
        min_length=8,
        style={"input_type": "password"},
        help_text="Minimo 8 caracteres. Se valida con las reglas de Django.",
    )
    password2 = serializers.CharField(
        write_only=True,
        style={"input_type": "password"},
        help_text="Repeticion de la contrasena.",
    )
    email = serializers.EmailField(required=True)
    rol = serializers.ChoiceField(
        choices=ROLES, write_only=True,
        help_text="Cargo con el que el usuario entra al sistema; define sus permisos.",
    )
    empleado = serializers.PrimaryKeyRelatedField(
        queryset=Empleado.objects.filter(usuario__isnull=True),
        required=False, allow_null=True, write_only=True,
        help_text="Empleado al que se le asigna esta cuenta (opcional).",
    )

    class Meta:
        model = User
        fields = [
            "username", "email", "first_name", "last_name",
            "password", "password2", "rol", "empleado",
        ]

    def validate_username(self, valor):
        if User.objects.filter(username__iexact=valor).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese nombre.")
        return valor

    def validate_email(self, valor):
        if User.objects.filter(email__iexact=valor).exists():
            raise serializers.ValidationError("Ya existe un usuario con ese correo.")
        return valor

    def validate(self, datos):
        if datos["password"] != datos["password2"]:
            raise serializers.ValidationError(
                {"password2": "Las contrasenas no coinciden."}
            )
        # Reglas de Django: longitud minima, no numerica, no comun,
        # no parecida al nombre de usuario.
        validate_password(datos["password"])
        return datos

    def create(self, datos):
        datos.pop("password2")
        rol = datos.pop("rol")
        empleado = datos.pop("empleado", None)
        # create_user aplica el hash a la contrasena. Nunca se guarda en claro.
        usuario = User.objects.create_user(**datos)
        usuario.groups.add(Group.objects.get_or_create(name=rol)[0])
        if empleado:
            empleado.usuario = usuario
            empleado.save(update_fields=["usuario"])
        return usuario


class UsuarioSerializer(serializers.ModelSerializer):
    """Representacion publica de un usuario. No expone la contrasena.

    Incluye el cargo y la matriz de permisos: el front-end la usa para
    mostrar solo los menus y botones que el cargo puede usar.
    """

    rol = serializers.SerializerMethodField()
    permisos = serializers.SerializerMethodField()
    empleado = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id", "username", "email", "first_name", "last_name", "date_joined",
            "last_login", "is_active", "rol", "permisos", "empleado",
        ]
        read_only_fields = fields

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_rol(self, usuario):
        return rol_de(usuario)

    @extend_schema_field(serializers.DictField(child=serializers.ListField(child=serializers.CharField())))
    def get_permisos(self, usuario):
        return permisos_de(usuario)

    @extend_schema_field(serializers.CharField(allow_null=True))
    def get_empleado(self, usuario):
        empleado = getattr(usuario, "empleado", None)
        return empleado.nombre_completo if empleado else None


class LoginSerializer(serializers.Serializer):
    """Credenciales de inicio de sesion."""

    username = serializers.CharField(help_text="Nombre de usuario registrado.")
    password = serializers.CharField(
        write_only=True, style={"input_type": "password"}
    )


# ==========================================================
# MODULOS DEL SISTEMA
# ==========================================================

class ClienteSerializer(serializers.ModelSerializer):

    class Meta:
        model = Cliente
        fields = ["id", "documento", "nombre", "correo", "telefono", "empresa"]

    def validate_documento(self, valor):
        if not valor.strip().isdigit():
            raise serializers.ValidationError("El documento solo admite digitos.")
        return valor.strip()


class ProveedorSerializer(serializers.ModelSerializer):

    class Meta:
        model = Proveedor
        fields = [
            "id", "nit", "empresa", "contacto",
            "correo", "telefono", "ciudad", "direccion",
        ]


class ProductoSerializer(serializers.ModelSerializer):
    """Incluye dos campos derivados que la interfaz necesita.

    proveedor_nombre evita que el cliente tenga que pedir el proveedor
    aparte solo para mostrar su nombre en una tabla.
    """

    proveedor_nombre = serializers.CharField(
        source="proveedor.empresa", read_only=True
    )
    stock_bajo = serializers.BooleanField(read_only=True)

    class Meta:
        model = Producto
        fields = [
            "id", "codigo", "nombre", "categoria",
            "proveedor", "proveedor_nombre",
            "precio_compra", "precio_venta",
            "stock", "stock_minimo", "stock_bajo",
        ]

    def validate(self, datos):
        """El precio de venta no puede ser inferior al de compra.

        Es una regla de negocio, no de formato: vender por debajo del costo
        suele ser un error de digitacion antes que una decision comercial.
        """
        compra = datos.get("precio_compra", getattr(self.instance, "precio_compra", None))
        venta = datos.get("precio_venta", getattr(self.instance, "precio_venta", None))
        if compra is not None and venta is not None and venta < compra:
            raise serializers.ValidationError(
                {"precio_venta": "El precio de venta no puede ser menor que el de compra."}
            )
        return datos


class EmpleadoSerializer(serializers.ModelSerializer):

    nombre_completo = serializers.CharField(read_only=True)

    class Meta:
        model = Empleado
        fields = [
            "id", "documento", "nombres", "apellidos", "nombre_completo",
            "correo", "telefono", "cargo", "area", "estado",
            "fecha_ingreso", "fecha_creacion",
        ]
        read_only_fields = ["fecha_creacion"]


class DetalleVentaSerializer(serializers.ModelSerializer):

    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)

    class Meta:
        model = DetalleVenta
        fields = [
            "id", "producto", "producto_nombre",
            "cantidad", "precio_unitario", "subtotal",
        ]
        read_only_fields = ["precio_unitario", "subtotal"]


class VentaSerializer(serializers.ModelSerializer):
    """Lectura de una venta con sus detalles y los nombres resueltos."""

    cliente_nombre = serializers.CharField(source="cliente.nombre", read_only=True)
    empleado_nombre = serializers.CharField(
        source="empleado.nombre_completo", read_only=True, default=None
    )
    detalles = DetalleVentaSerializer(many=True, read_only=True)

    class Meta:
        model = Venta
        fields = [
            "id", "cliente", "cliente_nombre",
            "empleado", "empleado_nombre",
            "fecha", "total", "estado", "detalles",
        ]
        read_only_fields = ["total", "fecha"]


class ResumenSerializer(serializers.Serializer):
    """Indicadores agregados del panel de control.

    No corresponde a ninguna tabla: es la forma de la respuesta del
    servicio de resumen, declarada para que quede documentada en el
    esquema OpenAPI.
    """

    clientes = serializers.IntegerField()
    proveedores = serializers.IntegerField()
    productos = serializers.IntegerField()
    empleados = serializers.IntegerField()
    ventas = serializers.IntegerField()
    total_vendido = serializers.DecimalField(max_digits=14, decimal_places=2)
    productos_stock_bajo = serializers.IntegerField()


class RegistrarVentaSerializer(serializers.Serializer):
    """Entrada del servicio de registro de una venta.

    No es un ModelSerializer porque la operacion no crea un solo objeto:
    crea la venta, su detalle y descuenta el inventario. Esa logica vive en
    core/servicios.py y se comparte con la capa web.
    """

    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    empleado = serializers.PrimaryKeyRelatedField(
        queryset=Empleado.objects.all(), required=False, allow_null=True
    )
    cantidad = serializers.IntegerField(min_value=1)

    def validate(self, datos):
        """Comprobacion temprana de existencias.

        No sustituye al descuento condicional del servicio —entre esta
        validacion y la escritura otro usuario puede vender—, pero permite
        devolver un mensaje claro en el caso normal.
        """
        producto = datos["producto"]
        if datos["cantidad"] > producto.stock:
            raise serializers.ValidationError({
                "cantidad": f"Solo hay {producto.stock} unidades de {producto.nombre}."
            })
        return datos


# ==========================================================
# PRODUCCION DIARIA (HU-001)
# ==========================================================

class ProduccionSerializer(serializers.ModelSerializer):
    """Registro de produccion de un turno.

    registrado_por no se recibe del cliente: la vista lo toma del token, para
    que nadie pueda registrar produccion a nombre de otro usuario.
    """

    material_nombre = serializers.CharField(source="get_material_display", read_only=True)
    turno_nombre = serializers.CharField(source="get_turno_display", read_only=True)
    supervisor_nombre = serializers.CharField(
        source="supervisor.nombre_completo", read_only=True, default=None
    )
    registrado_por = serializers.CharField(source="registrado_por.username", read_only=True, default=None)

    class Meta:
        model = RegistroProduccion
        fields = [
            "id", "fecha", "turno", "turno_nombre", "material", "material_nombre",
            "cantidad", "unidad", "supervisor", "supervisor_nombre", "observaciones",
            "registrado_por", "fecha_registro",
        ]
        read_only_fields = ["fecha_registro"]

    def validate_fecha(self, valor):
        if valor > timezone.localdate():
            raise serializers.ValidationError("La fecha de producción no puede ser posterior a hoy.")
        return valor


class StockMateriaPrimaSerializer(serializers.Serializer):
    material = serializers.CharField()
    material_nombre = serializers.CharField()
    unidad = serializers.CharField()
    total = serializers.DecimalField(max_digits=12, decimal_places=2)


# ==========================================================
# SEGURIDAD
# ==========================================================

class RegistroAccesoSerializer(serializers.ModelSerializer):
    evento_nombre = serializers.CharField(source="get_evento_display", read_only=True)

    class Meta:
        model = RegistroAcceso
        fields = ["id", "nombre_usuario", "evento", "evento_nombre", "fecha", "ip", "navegador", "token_jti"]
        read_only_fields = fields


class CambiarRolSerializer(serializers.Serializer):
    rol = serializers.ChoiceField(choices=ROLES)


# ==========================================================
# CRM
# ==========================================================

class OportunidadSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source="cliente.nombre", read_only=True)
    responsable_nombre = serializers.CharField(
        source="responsable.nombre_completo", read_only=True, default=None
    )
    etapa_nombre = serializers.CharField(source="get_etapa_display", read_only=True)
    probabilidad = serializers.IntegerField(read_only=True)
    valor_ponderado = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = Oportunidad
        fields = [
            "id", "cliente", "cliente_nombre", "titulo", "etapa", "etapa_nombre",
            "valor_estimado", "probabilidad", "valor_ponderado",
            "responsable", "responsable_nombre", "fecha_cierre_estimada", "notas",
            "creado", "actualizado",
        ]
        read_only_fields = ["creado", "actualizado"]


class InteraccionSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source="cliente.nombre", read_only=True)
    tipo_nombre = serializers.CharField(source="get_tipo_display", read_only=True)
    registrado_por = serializers.CharField(source="registrado_por.username", read_only=True, default=None)

    class Meta:
        model = Interaccion
        fields = [
            "id", "cliente", "cliente_nombre", "oportunidad", "tipo", "tipo_nombre",
            "fecha", "descripcion", "proxima_accion", "registrado_por",
        ]

    def validate(self, datos):
        oportunidad = datos.get("oportunidad")
        cliente = datos.get("cliente", getattr(self.instance, "cliente", None))
        if oportunidad and cliente and oportunidad.cliente_id != cliente.pk:
            raise serializers.ValidationError(
                {"oportunidad": "La oportunidad pertenece a otro cliente."}
            )
        return datos


# ==========================================================
# TIENDA Y PAGOS
# ==========================================================

class ItemPedidoSerializer(serializers.ModelSerializer):
    producto_nombre = serializers.CharField(source="producto.nombre", read_only=True)
    subtotal = serializers.DecimalField(max_digits=14, decimal_places=2, read_only=True)

    class Meta:
        model = ItemPedido
        fields = ["id", "producto", "producto_nombre", "cantidad", "precio_unitario", "subtotal"]
        read_only_fields = ["precio_unitario"]


class PedidoSerializer(serializers.ModelSerializer):
    cliente_nombre = serializers.CharField(source="cliente.nombre", read_only=True)
    estado_nombre = serializers.CharField(source="get_estado_display", read_only=True)
    items = ItemPedidoSerializer(many=True, read_only=True)

    class Meta:
        model = Pedido
        fields = [
            "id", "cliente", "cliente_nombre", "estado", "estado_nombre", "total",
            "metodo_pago", "venta", "creado", "pagado_en", "items",
        ]
        read_only_fields = fields


class LineaCarritoSerializer(serializers.Serializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    cantidad = serializers.IntegerField(min_value=1, max_value=10000)


class CrearPedidoSerializer(serializers.Serializer):
    cliente = serializers.PrimaryKeyRelatedField(queryset=Cliente.objects.all())
    items = LineaCarritoSerializer(many=True, allow_empty=False)


# ==========================================================
# NORMATIVA Y MEJORA CONTINUA
# ==========================================================

class RequisitoNormativoSerializer(serializers.ModelSerializer):
    autoridad_nombre = serializers.CharField(source="get_autoridad_display", read_only=True)
    categoria_nombre = serializers.CharField(source="get_categoria_display", read_only=True)
    estado_nombre = serializers.CharField(source="get_estado_display", read_only=True)
    responsable_nombre = serializers.CharField(
        source="responsable.nombre_completo", read_only=True, default=None
    )
    dias_para_vencer = serializers.IntegerField(read_only=True)
    alerta = serializers.CharField(read_only=True)

    class Meta:
        model = RequisitoNormativo
        fields = [
            "id", "autoridad", "autoridad_nombre", "categoria", "categoria_nombre",
            "nombre", "norma", "descripcion", "periodicidad", "fecha_vencimiento",
            "estado", "estado_nombre", "responsable", "responsable_nombre",
            "evidencia", "dias_para_vencer", "alerta", "actualizado",
        ]
        read_only_fields = ["actualizado"]


class AccionMejoraSerializer(serializers.ModelSerializer):
    origen_nombre = serializers.CharField(source="get_origen_display", read_only=True)
    responsable_nombre = serializers.CharField(
        source="responsable.nombre_completo", read_only=True, default=None
    )
    creado_por = serializers.CharField(source="creado_por.username", read_only=True, default=None)

    class Meta:
        model = AccionMejora
        fields = [
            "id", "titulo", "origen", "origen_nombre", "tipo", "descripcion",
            "causa_raiz", "plan_accion", "fase", "responsable", "responsable_nombre",
            "fecha_compromiso", "resultado", "creado_por", "creado", "actualizado",
        ]
        read_only_fields = ["creado", "actualizado"]

    def validate(self, datos):
        # No se cierra una accion sin verificar que funciono: es el paso que
        # convierte una lista de tareas en mejora continua de verdad.
        fase = datos.get("fase", getattr(self.instance, "fase", "Planear"))
        resultado = datos.get("resultado", getattr(self.instance, "resultado", ""))
        if fase == "Cerrada" and not (resultado or "").strip():
            raise serializers.ValidationError(
                {"resultado": "Para cerrar la acción registre la verificación de su eficacia."}
            )
        return datos
