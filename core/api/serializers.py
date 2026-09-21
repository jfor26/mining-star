"""
Serializadores de la API REST de Mining Star.

Un serializador cumple en la API el mismo papel que un ModelForm en la capa
web: traduce entre los objetos de Python y el JSON que viaja por la red, y
—sobre todo— valida la entrada ANTES de que toque la base de datos.

Las reglas de validacion se derivan del modelo siempre que es posible, para
que no existan dos definiciones del mismo limite que puedan divergir.
"""

from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers

from ..models import Cliente, DetalleVenta, Empleado, Producto, Proveedor, Venta

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

    class Meta:
        model = User
        fields = ["username", "email", "first_name", "last_name", "password", "password2"]

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
        # create_user aplica el hash a la contrasena. Nunca se guarda en claro.
        return User.objects.create_user(**datos)


class UsuarioSerializer(serializers.ModelSerializer):
    """Representacion publica de un usuario. No expone la contrasena."""

    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name", "date_joined"]
        read_only_fields = fields


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
