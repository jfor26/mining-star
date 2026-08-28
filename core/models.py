from django.db import models


# ==========================================
# CLIENTES
# ==========================================

class Cliente(models.Model):

    documento = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=150)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)
    empresa = models.CharField(max_length=150)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


# ==========================================
# PROVEEDORES
# ==========================================

class Proveedor(models.Model):

    nit = models.CharField(max_length=20, unique=True)
    empresa = models.CharField(max_length=150)
    contacto = models.CharField(max_length=150)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)
    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)

    class Meta:
        ordering = ["empresa"]

    def __str__(self):
        return self.empresa


# ==========================================
# PRODUCTOS
# ==========================================

class Producto(models.Model):

    codigo = models.CharField(max_length=20, unique=True)

    nombre = models.CharField(max_length=150)

    categoria = models.CharField(max_length=100)

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.CASCADE
    )

    precio_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    precio_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    stock = models.IntegerField()

    stock_minimo = models.IntegerField(default=5)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


# ==========================================
# EMPLEADOS
# ==========================================

class Empleado(models.Model):

    CARGOS = [
        ("Administrador", "Administrador"),
        ("Supervisor", "Supervisor"),
        ("Operario", "Operario"),
        ("Contador", "Contador"),
        ("Auxiliar", "Auxiliar"),
    ]

    AREAS = [
        ("Gerencia", "Gerencia"),
        ("Operaciones", "Operaciones"),
        ("Recursos Humanos", "Recursos Humanos"),
        ("Seguridad Industrial", "Seguridad Industrial"),
        ("Finanzas", "Finanzas"),
        ("Logística", "Logística"),
    ]

    ESTADOS = [
        ("Activo", "Activo"),
        ("Vacaciones", "Vacaciones"),
        ("Inactivo", "Inactivo"),
    ]

    documento = models.CharField(
        max_length=20,
        unique=True
    )

    nombres = models.CharField(
        max_length=100
    )

    apellidos = models.CharField(
        max_length=100
    )

    correo = models.EmailField()

    telefono = models.CharField(
        max_length=20
    )

    cargo = models.CharField(
        max_length=30,
        choices=CARGOS
    )

    area = models.CharField(
        max_length=50,
        choices=AREAS
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="Activo"
    )

    fecha_ingreso = models.DateField(
        auto_now_add=True
    )

    fecha_creacion = models.DateTimeField(
        auto_now_add=True
    )

    class Meta:
        ordering = ["nombres", "apellidos"]

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"
    # ==========================================
# VENTAS
# ==========================================

class Venta(models.Model):

    ESTADOS = [
        ("Completada", "Completada"),
        ("Pendiente", "Pendiente"),
        ("Anulada", "Anulada"),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="ventas"
    )

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="ventas",
        null=True,
        blank=True
    )

    fecha = models.DateTimeField(
        auto_now_add=True
    )

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0
    )

    estado = models.CharField(
        max_length=20,
        choices=ESTADOS,
        default="Completada"
    )

    class Meta:
        ordering = ["-fecha"]

    def __str__(self):
        return f"Venta #{self.id} - {self.cliente.nombre}"
    # ==========================================
# DETALLE DE VENTAS
# ==========================================

class DetalleVenta(models.Model):

    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name="detalles"
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="detalles_venta"
    )

    cantidad = models.PositiveIntegerField()

    precio_unitario = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2
    )

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} unidades"