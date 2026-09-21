"""
Modelos de datos de Mining Star.

Cada modelo representa una tabla. Las validaciones se declaran aqui
(y no solo en el formulario o en el HTML) porque este es el unico punto
por el que pasan TODAS las escrituras: admin, formularios, shell y scripts.
"""

from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

# ==========================================================
# CLIENTES
# ==========================================================

class Cliente(models.Model):

    documento = models.CharField(max_length=20, unique=True, db_index=True)
    nombre = models.CharField(max_length=150)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)
    empresa = models.CharField(max_length=150)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "cliente"
        verbose_name_plural = "clientes"

    def __str__(self):
        return self.nombre


# ==========================================================
# PROVEEDORES
# ==========================================================

class Proveedor(models.Model):

    nit = models.CharField(max_length=20, unique=True, db_index=True)
    empresa = models.CharField(max_length=150)
    contacto = models.CharField(max_length=150)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)
    ciudad = models.CharField(max_length=100)
    direccion = models.CharField(max_length=200)

    class Meta:
        ordering = ["empresa"]
        verbose_name = "proveedor"
        verbose_name_plural = "proveedores"

    def __str__(self):
        return self.empresa


# ==========================================================
# PRODUCTOS
# ==========================================================

class Producto(models.Model):

    codigo = models.CharField(max_length=20, unique=True, db_index=True)
    nombre = models.CharField(max_length=150)
    categoria = models.CharField(max_length=100)

    proveedor = models.ForeignKey(
        Proveedor,
        on_delete=models.PROTECT,
        related_name="productos",
    )

    precio_compra = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )

    precio_venta = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0"))],
    )

    # PositiveIntegerField impide a nivel de base de datos que el stock
    # quede negativo, pase lo que pase en el codigo.
    stock = models.PositiveIntegerField(default=0)
    stock_minimo = models.PositiveIntegerField(default=5)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "producto"
        verbose_name_plural = "productos"

    def __str__(self):
        return self.nombre

    @property
    def stock_bajo(self):
        """True si el producto llego a su nivel minimo de inventario."""
        return self.stock <= self.stock_minimo


# ==========================================================
# EMPLEADOS
# ==========================================================

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

    documento = models.CharField(max_length=20, unique=True, db_index=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20)

    cargo = models.CharField(max_length=30, choices=CARGOS)
    area = models.CharField(max_length=50, choices=AREAS)
    estado = models.CharField(max_length=20, choices=ESTADOS, default="Activo")

    # La fecha de ingreso la decide el usuario: un empleado puede haber
    # entrado antes de que se registrara en el sistema.
    # (Antes era auto_now_add=True, lo que la forzaba a "hoy" y la hacia
    #  imposible de editar.)
    fecha_ingreso = models.DateField(default=timezone.localdate)

    # Esta si es automatica: marca cuando se creo el registro.
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombres", "apellidos"]
        verbose_name = "empleado"
        verbose_name_plural = "empleados"

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

    @property
    def nombre_completo(self):
        return f"{self.nombres} {self.apellidos}"


# ==========================================================
# VENTAS
# ==========================================================

class Venta(models.Model):

    ESTADOS = [
        ("Completada", "Completada"),
        ("Pendiente", "Pendiente"),
        ("Anulada", "Anulada"),
    ]

    cliente = models.ForeignKey(
        Cliente,
        on_delete=models.PROTECT,
        related_name="ventas",
    )

    empleado = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="ventas",
        null=True,
        blank=True,
    )

    fecha = models.DateTimeField(default=timezone.now)

    total = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal("0"),
        validators=[MinValueValidator(Decimal("0"))],
    )

    estado = models.CharField(max_length=20, choices=ESTADOS, default="Completada")

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "venta"
        verbose_name_plural = "ventas"

    def __str__(self):
        return f"Venta #{self.pk} - {self.cliente.nombre}"

    def recalcular_total(self):
        """Recalcula el total sumando los subtotales de sus detalles."""
        total = sum(
            (detalle.subtotal for detalle in self.detalles.all()),
            Decimal("0"),
        )
        self.total = total
        self.save(update_fields=["total"])
        return total


# ==========================================================
# DETALLE DE VENTAS
# ==========================================================

class DetalleVenta(models.Model):

    venta = models.ForeignKey(
        Venta,
        on_delete=models.CASCADE,
        related_name="detalles",
    )

    producto = models.ForeignKey(
        Producto,
        on_delete=models.PROTECT,
        related_name="detalles_venta",
    )

    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        ordering = ["id"]
        verbose_name = "detalle de venta"
        verbose_name_plural = "detalles de venta"

    def __str__(self):
        return f"{self.producto.nombre} - {self.cantidad} unidades"

    def save(self, *args, **kwargs):
        # El subtotal siempre se deriva de cantidad x precio: asi nunca
        # puede quedar desincronizado por un error de calculo en la vista.
        self.subtotal = Decimal(self.cantidad) * self.precio_unitario
        super().save(*args, **kwargs)


# ==========================================================
# PRODUCCION DIARIA DE LA MINA  (historia de usuario HU-001)
# ==========================================================

class RegistroProduccion(models.Model):
    """Material extraido en la mina durante un turno.

    HU-001: "Como Supervisor de Mina, quiero registrar la cantidad y tipo de
    material extraido por turno para llevar un control preciso de la
    produccion y actualizar el inventario de materia prima."

    El stock de materia prima no se guarda en una columna aparte: se calcula
    sumando estos registros (ver servicios.stock_materia_prima). Asi no
    existen dos cifras que puedan contradecirse.
    """

    TURNOS = [
        ("Manana", "Mañana (6:00 - 14:00)"),
        ("Tarde", "Tarde (14:00 - 22:00)"),
        ("Noche", "Noche (22:00 - 6:00)"),
    ]

    # Lista predefinida que exige el criterio de aceptacion de la HU-001.
    MATERIALES = [
        ("Marmol", "Mármol"),
        ("Caliza", "Caliza"),
        ("Recebo", "Recebo"),
    ]

    UNIDADES = [
        ("t", "Toneladas (t)"),
        ("m3", "Metros cúbicos (m³)"),
    ]

    fecha = models.DateField(default=timezone.localdate)
    turno = models.CharField(max_length=10, choices=TURNOS)
    material = models.CharField(max_length=10, choices=MATERIALES)
    unidad = models.CharField(max_length=2, choices=UNIDADES, default="t")

    # Minimo 0,01: un registro en cero no aporta informacion y suele ser
    # un error de digitacion. Maximo 5.000 por turno: la cantera no extrae
    # esa cifra en ocho horas; un valor mayor es casi seguro un cero de mas.
    cantidad = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        validators=[MinValueValidator(Decimal("0.01")), MaxValueValidator(Decimal("5000"))],
    )

    supervisor = models.ForeignKey(
        Empleado,
        on_delete=models.PROTECT,
        related_name="producciones",
        null=True,
        blank=True,
    )
    observaciones = models.CharField(max_length=300, blank=True)

    # Quien lo registro en el sistema (usuario autenticado) y cuando.
    registrado_por = models.ForeignKey(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="producciones_registradas",
    )
    fecha_registro = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-fecha", "turno", "material"]
        verbose_name = "registro de producción"
        verbose_name_plural = "registros de producción"
        constraints = [
            # Un mismo material no se registra dos veces en el mismo turno:
            # duplicarlo inflaria la produccion y el stock de materia prima.
            models.UniqueConstraint(
                fields=["fecha", "turno", "material"],
                name="produccion_unica_por_turno",
                violation_error_message=(
                    "Ya existe un registro de ese material para ese turno y esa fecha."
                ),
            ),
        ]

    def __str__(self):
        return f"{self.get_material_display()} - {self.fecha:%d/%m/%Y} - {self.get_turno_display()}"

    def clean(self):
        """La produccion es un hecho ocurrido: no puede tener fecha futura."""
        super().clean()
        if self.fecha and self.fecha > timezone.localdate():
            raise ValidationError({"fecha": "La fecha de producción no puede ser posterior a hoy."})
