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
    # Cuenta para el portal de clientes (opcional). El usuario es el NIT o
    # documento del cliente y pertenece al grupo "Cliente".
    usuario = models.OneToOneField(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="cliente",
    )

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

    # Los cargos coinciden con los roles de core/permisos.py: el cargo de un
    # empleado determina que puede hacer cuando usa el sistema.
    CARGOS = [
        ("Gerente", "Gerente"),
        ("Administrador", "Administrador"),
        ("Supervisor", "Supervisor"),
        ("Comercial", "Comercial"),
        ("Contador", "Contador"),
        ("Operario", "Operario"),
        ("Auxiliar", "Auxiliar"),
    ]

    AREAS = [
        ("Gerencia", "Gerencia"),
        ("Operaciones", "Operaciones"),
        ("Recursos Humanos", "Recursos Humanos"),
        ("Seguridad Industrial", "Seguridad Industrial"),
        ("Finanzas", "Finanzas"),
        ("Logística", "Logística"),
        ("Comercial", "Comercial"),
        ("Gestión Ambiental", "Gestión Ambiental"),
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

    # Cuenta con la que el empleado entra al sistema. Es opcional: un
    # operario puede no usar el aplicativo. Si se borra el usuario, el
    # empleado se conserva (SET_NULL) porque tiene historial laboral.
    usuario = models.OneToOneField(
        "auth.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="empleado",
    )

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
        # El panel agrupa ventas por mes y filtra por estado: sin indice,
        # cada consulta recorre la tabla completa.
        indexes = [models.Index(fields=["estado", "fecha"], name="venta_estado_fecha_idx")]

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


# ==========================================================
# SEGURIDAD: REGISTRO DE ACCESOS
# ==========================================================

class RegistroAcceso(models.Model):
    """Bitacora de cada intento de ingreso al sistema.

    Cada vez que un empleado inicia sesion se emite un token de acceso (JWT)
    y aqui queda constancia de quien, cuando, desde donde y con que token
    (su identificador jti, nunca el token completo). Los intentos fallidos
    tambien se guardan: son la base del bloqueo por fuerza bruta.
    """

    EVENTOS = [
        ("ingreso", "Ingreso exitoso"),
        ("fallido", "Intento fallido"),
        ("bloqueado", "Bloqueado por intentos"),
        ("salida", "Cierre de sesión"),
    ]

    usuario = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True,
        related_name="accesos",
    )
    # Se guarda el nombre escrito aunque no exista el usuario: asi se ven los
    # intentos contra cuentas inventadas.
    nombre_usuario = models.CharField(max_length=150)
    evento = models.CharField(max_length=10, choices=EVENTOS)
    fecha = models.DateTimeField(auto_now_add=True, db_index=True)
    ip = models.GenericIPAddressField(null=True, blank=True)
    navegador = models.CharField(max_length=255, blank=True)
    token_jti = models.CharField("identificador del token", max_length=64, blank=True)

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "registro de acceso"
        verbose_name_plural = "registros de acceso"
        indexes = [models.Index(fields=["nombre_usuario", "evento", "fecha"], name="acceso_usuario_idx")]

    def __str__(self):
        return f"{self.nombre_usuario} - {self.get_evento_display()} - {self.fecha:%d/%m/%Y %H:%M}"


# ==========================================================
# CRM: OPORTUNIDADES E INTERACCIONES CON CLIENTES
# ==========================================================

class Oportunidad(models.Model):
    """Negocio posible con un cliente, desde el primer contacto hasta el cierre."""

    ETAPAS = [
        ("Prospecto", "Prospecto"),
        ("Contactado", "Contactado"),
        ("Cotizacion", "Cotización enviada"),
        ("Negociacion", "Negociación"),
        ("Ganada", "Ganada"),
        ("Perdida", "Perdida"),
    ]

    # Probabilidad de cierre sugerida por etapa, para el valor ponderado.
    PROBABILIDAD_POR_ETAPA = {
        "Prospecto": 10, "Contactado": 25, "Cotizacion": 50,
        "Negociacion": 75, "Ganada": 100, "Perdida": 0,
    }

    ORIGENES = [("Interno", "Registrada por el equipo"), ("Portal", "Solicitud desde el portal")]

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="oportunidades")
    titulo = models.CharField(max_length=150)
    origen = models.CharField(max_length=8, choices=ORIGENES, default="Interno")
    etapa = models.CharField(max_length=12, choices=ETAPAS, default="Prospecto", db_index=True)
    valor_estimado = models.DecimalField(
        max_digits=14, decimal_places=2, validators=[MinValueValidator(Decimal("0"))],
    )
    responsable = models.ForeignKey(
        Empleado, on_delete=models.SET_NULL, null=True, blank=True, related_name="oportunidades",
    )
    fecha_cierre_estimada = models.DateField(null=True, blank=True)
    notas = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-actualizado"]
        verbose_name = "oportunidad"
        verbose_name_plural = "oportunidades"

    def __str__(self):
        return f"{self.titulo} ({self.cliente})"

    @property
    def probabilidad(self):
        return self.PROBABILIDAD_POR_ETAPA[self.etapa]

    @property
    def valor_ponderado(self):
        return (self.valor_estimado * self.probabilidad / 100).quantize(Decimal("0.01"))


class Interaccion(models.Model):
    """Contacto registrado con un cliente: llamada, visita, correo..."""

    TIPOS = [
        ("Llamada", "Llamada"),
        ("Correo", "Correo"),
        ("Visita", "Visita"),
        ("Reunion", "Reunión"),
        ("WhatsApp", "WhatsApp"),
        ("Portal", "Portal de clientes"),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.CASCADE, related_name="interacciones")
    oportunidad = models.ForeignKey(
        Oportunidad, on_delete=models.SET_NULL, null=True, blank=True, related_name="interacciones",
    )
    tipo = models.CharField(max_length=10, choices=TIPOS)
    fecha = models.DateTimeField(default=timezone.now)
    descripcion = models.CharField(max_length=500)
    proxima_accion = models.CharField("próxima acción", max_length=200, blank=True)
    registrado_por = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="interacciones",
    )

    class Meta:
        ordering = ["-fecha"]
        verbose_name = "interacción"
        verbose_name_plural = "interacciones"

    def __str__(self):
        return f"{self.get_tipo_display()} con {self.cliente} - {self.fecha:%d/%m/%Y}"


# ==========================================================
# TIENDA: PEDIDOS DEL CARRITO Y PAGOS CON STRIPE
# ==========================================================

class Pedido(models.Model):
    """Pedido armado en el carrito de compras.

    No descuenta inventario al crearse: un carrito abandonado no debe
    bloquear existencias. El descuento ocurre al confirmarse el pago, cuando
    el pedido se convierte en una Venta (ver servicios.confirmar_pago).
    """

    ESTADOS = [
        ("Pendiente", "Pendiente de pago"),
        ("Pagado", "Pagado"),
        ("Cancelado", "Cancelado"),
        ("Fallido", "Pago fallido"),
    ]

    METODOS = [
        ("stripe", "Stripe (tarjeta)"),
        ("simulado", "Pago simulado (demostración)"),
    ]

    cliente = models.ForeignKey(Cliente, on_delete=models.PROTECT, related_name="pedidos")
    estado = models.CharField(max_length=10, choices=ESTADOS, default="Pendiente", db_index=True)
    total = models.DecimalField(max_digits=14, decimal_places=2, default=Decimal("0"))
    metodo_pago = models.CharField(max_length=10, choices=METODOS, blank=True)
    referencia_pago = models.CharField(
        "referencia de la pasarela", max_length=255, blank=True, db_index=True,
    )
    venta = models.OneToOneField(
        Venta, on_delete=models.SET_NULL, null=True, blank=True, related_name="pedido",
    )
    creado_por = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="pedidos",
    )
    creado = models.DateTimeField(auto_now_add=True)
    pagado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "pedido"
        verbose_name_plural = "pedidos"

    def __str__(self):
        return f"Pedido #{self.pk} - {self.cliente}"


class ItemPedido(models.Model):
    pedido = models.ForeignKey(Pedido, on_delete=models.CASCADE, related_name="items")
    producto = models.ForeignKey(Producto, on_delete=models.PROTECT, related_name="items_pedido")
    cantidad = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    # El precio se congela al crear el pedido: si luego cambia el catalogo,
    # el cliente paga lo que vio en el carrito.
    precio_unitario = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        ordering = ["id"]
        verbose_name = "ítem de pedido"
        verbose_name_plural = "ítems de pedido"
        constraints = [
            models.UniqueConstraint(fields=["pedido", "producto"], name="producto_unico_por_pedido"),
        ]

    def __str__(self):
        return f"{self.producto} x {self.cantidad}"

    @property
    def subtotal(self):
        return self.precio_unitario * self.cantidad


# ==========================================================
# REPOSITORIO DE REQUISITOS MINEROS Y AMBIENTALES
# ==========================================================

class RequisitoNormativo(models.Model):
    """Obligacion legal que la empresa debe cumplir y su estado.

    Reune en un solo lugar lo que exigen la autoridad minera (ANM), la
    autoridad ambiental (CORTOLIMA) y las demas entidades, con su
    vencimiento, para que nada se venza sin que alguien lo sepa.
    """

    AUTORIDADES = [
        ("ANM", "Agencia Nacional de Minería (ANM)"),
        ("CORTOLIMA", "CORTOLIMA (autoridad ambiental regional)"),
        ("MinEnergia", "Ministerio de Minas y Energía"),
        ("MinAmbiente", "Ministerio de Ambiente"),
        ("MinTrabajo", "Ministerio del Trabajo"),
        ("DIAN", "DIAN"),
        ("Municipio", "Alcaldía municipal"),
        ("SIC", "Superintendencia de Industria y Comercio"),
    ]

    CATEGORIAS = [
        ("Minero", "Minero"),
        ("Ambiental", "Ambiental"),
        ("SST", "Seguridad y salud en el trabajo"),
        ("Tributario", "Tributario"),
        ("Datos", "Protección de datos"),
    ]

    ESTADOS = [
        ("Cumplido", "Cumplido"),
        ("EnTramite", "En trámite"),
        ("Pendiente", "Pendiente"),
        ("Vencido", "Vencido"),
    ]

    autoridad = models.CharField(max_length=12, choices=AUTORIDADES)
    categoria = models.CharField(max_length=12, choices=CATEGORIAS, db_index=True)
    nombre = models.CharField(max_length=200)
    norma = models.CharField("norma de referencia", max_length=200)
    descripcion = models.TextField()
    periodicidad = models.CharField(max_length=60, blank=True)
    fecha_vencimiento = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADOS, default="Pendiente", db_index=True)
    responsable = models.ForeignKey(
        Empleado, on_delete=models.SET_NULL, null=True, blank=True, related_name="requisitos",
    )
    evidencia = models.CharField("evidencia o radicado", max_length=300, blank=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["fecha_vencimiento", "nombre"]
        verbose_name = "requisito normativo"
        verbose_name_plural = "requisitos normativos"

    def __str__(self):
        return self.nombre

    @property
    def dias_para_vencer(self):
        if not self.fecha_vencimiento:
            return None
        return (self.fecha_vencimiento - timezone.localdate()).days

    @property
    def alerta(self):
        """'vencido', 'proximo' (30 dias o menos) u 'ok'."""
        if self.estado == "Cumplido":
            return "ok"
        dias = self.dias_para_vencer
        if dias is None:
            return "ok"
        if dias < 0:
            return "vencido"
        return "proximo" if dias <= 30 else "ok"


# ==========================================================
# MEJORA CONTINUA (CICLO PHVA)
# ==========================================================

class AccionMejora(models.Model):
    """Accion del sistema de mejora continua, organizada por el ciclo PHVA
    (Planear, Hacer, Verificar, Actuar)."""

    ORIGENES = [
        ("Auditoria", "Auditoría"),
        ("Cliente", "Queja o reclamo de cliente"),
        ("SST", "Incidente de SST"),
        ("Ambiental", "Hallazgo ambiental"),
        ("Empleado", "Sugerencia de empleado"),
        ("Indicador", "Indicador fuera de meta"),
    ]

    TIPOS = [
        ("Correctiva", "Correctiva"),
        ("Preventiva", "Preventiva"),
        ("Mejora", "Oportunidad de mejora"),
    ]

    FASES = [
        ("Planear", "Planear"),
        ("Hacer", "Hacer"),
        ("Verificar", "Verificar"),
        ("Actuar", "Actuar"),
        ("Cerrada", "Cerrada"),
    ]

    titulo = models.CharField(max_length=150)
    origen = models.CharField(max_length=10, choices=ORIGENES)
    tipo = models.CharField(max_length=10, choices=TIPOS, default="Mejora")
    descripcion = models.TextField("situación encontrada")
    causa_raiz = models.TextField("causa raíz", blank=True)
    plan_accion = models.TextField("plan de acción", blank=True)
    fase = models.CharField(max_length=10, choices=FASES, default="Planear", db_index=True)
    responsable = models.ForeignKey(
        Empleado, on_delete=models.SET_NULL, null=True, blank=True, related_name="acciones_mejora",
    )
    fecha_compromiso = models.DateField(null=True, blank=True)
    resultado = models.TextField("verificación de eficacia", blank=True)
    creado_por = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="acciones_mejora",
    )
    creado = models.DateTimeField(auto_now_add=True)
    actualizado = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "acción de mejora"
        verbose_name_plural = "acciones de mejora"

    def __str__(self):
        return self.titulo


# ==========================================================
# NOTIFICACIONES
# ==========================================================

class NotificacionLeida(models.Model):
    """Marca que un usuario ya leyo un aviso.

    Los avisos no se guardan: se calculan en cada consulta a partir del estado
    real del sistema (stock, requisitos, pedidos, CRM) en core/notificaciones.py.
    Cada aviso tiene una clave estable; aqui solo se registra cuales leyo cada
    usuario. Si la situacion cambia (por ejemplo, el stock baja otra vez), la
    clave cambia y el aviso vuelve a aparecer como nuevo.
    """

    usuario = models.ForeignKey("auth.User", on_delete=models.CASCADE, related_name="notificaciones_leidas")
    clave = models.CharField(max_length=120)
    leida_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["usuario", "clave"], name="notificacion_leida_unica")]
        verbose_name = "notificación leída"
        verbose_name_plural = "notificaciones leídas"

    def __str__(self):
        return f"{self.usuario} · {self.clave}"


# ==========================================================
# ATENCION AL CLIENTE: PQRS Y MENSAJES DE CONTACTO
# ==========================================================

class Pqrs(models.Model):
    """Peticion, queja, reclamo o sugerencia radicada desde el sitio publico
    o el portal. Se identifica con un radicado PQRS-AAAA-NNNN."""

    TIPOS = [("Peticion", "Petición"), ("Queja", "Queja"), ("Reclamo", "Reclamo"), ("Sugerencia", "Sugerencia")]
    ESTADOS = [("Recibida", "Recibida"), ("EnTramite", "En trámite"), ("Respondida", "Respondida"), ("Cerrada", "Cerrada")]

    radicado = models.CharField(max_length=20, unique=True, editable=False)
    tipo = models.CharField(max_length=10, choices=TIPOS)
    nombre = models.CharField(max_length=150)
    documento = models.CharField(max_length=20)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)
    detalle = models.TextField(max_length=2000)
    autoriza_datos = models.BooleanField(default=False)
    cliente = models.ForeignKey(Cliente, on_delete=models.SET_NULL, null=True, blank=True, related_name="pqrs")
    estado = models.CharField(max_length=10, choices=ESTADOS, default="Recibida", db_index=True)
    respuesta = models.TextField(blank=True)
    respondida_por = models.ForeignKey(
        "auth.User", on_delete=models.SET_NULL, null=True, blank=True, related_name="pqrs_respondidas",
    )
    creada = models.DateTimeField(auto_now_add=True)
    actualizada = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-creada"]
        verbose_name = "PQRS"
        verbose_name_plural = "PQRS"

    def __str__(self):
        return self.radicado

    def save(self, *args, **kwargs):
        # El radicado se asigna al crear: PQRS-<año>-<consecutivo del año>.
        if not self.radicado:
            anio = timezone.localdate().year
            ultimo = Pqrs.objects.filter(radicado__startswith=f"PQRS-{anio}-").order_by("-radicado").first()
            siguiente = int(ultimo.radicado.rsplit("-", 1)[1]) + 1 if ultimo else 1
            self.radicado = f"PQRS-{anio}-{siguiente:04d}"
        super().save(*args, **kwargs)


class MensajeContacto(models.Model):
    """Mensaje del formulario de contacto del sitio publico."""

    nombre = models.CharField(max_length=150)
    correo = models.EmailField()
    telefono = models.CharField(max_length=20, blank=True)
    mensaje = models.TextField(max_length=2000)
    atendido = models.BooleanField(default=False)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "mensaje de contacto"
        verbose_name_plural = "mensajes de contacto"

    def __str__(self):
        return f"{self.nombre} · {self.creado:%d/%m/%Y}"
