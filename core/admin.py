"""
Registro de modelos en el panel de administracion de Django.

Antes solo estaba registrado Cliente, asi que los otros cinco modelos
eran invisibles desde /admin/. Aqui se registran todos, cada uno con
columnas, buscador y filtros utiles.
"""

from django.contrib import admin

from .models import (
    Cliente,
    DetalleVenta,
    Empleado,
    Producto,
    Proveedor,
    RegistroProduccion,
    Venta,
)


@admin.register(Cliente)
class ClienteAdmin(admin.ModelAdmin):
    list_display = ("documento", "nombre", "empresa", "correo", "telefono")
    search_fields = ("documento", "nombre", "empresa", "correo")
    list_filter = ("empresa",)


@admin.register(Proveedor)
class ProveedorAdmin(admin.ModelAdmin):
    list_display = ("nit", "empresa", "contacto", "ciudad", "telefono")
    search_fields = ("nit", "empresa", "contacto")
    list_filter = ("ciudad",)


@admin.register(Producto)
class ProductoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo",
        "nombre",
        "categoria",
        "proveedor",
        "precio_venta",
        "stock",
        "stock_bajo",
    )
    search_fields = ("codigo", "nombre", "categoria")
    list_filter = ("categoria", "proveedor")
    # Evita una consulta extra por fila al mostrar el proveedor.
    list_select_related = ("proveedor",)

    @admin.display(boolean=True, description="Stock bajo")
    def stock_bajo(self, obj):
        return obj.stock_bajo


@admin.register(Empleado)
class EmpleadoAdmin(admin.ModelAdmin):
    list_display = (
        "documento",
        "nombre_completo",
        "cargo",
        "area",
        "estado",
        "fecha_ingreso",
    )
    search_fields = ("documento", "nombres", "apellidos", "correo")
    list_filter = ("estado", "area", "cargo")
    date_hierarchy = "fecha_ingreso"


class DetalleVentaInline(admin.TabularInline):
    """Permite ver y editar los renglones de una venta dentro de la venta."""
    model = DetalleVenta
    extra = 0
    readonly_fields = ("subtotal",)


@admin.register(Venta)
class VentaAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "empleado", "fecha", "total", "estado")
    search_fields = ("cliente__nombre", "cliente__documento")
    list_filter = ("estado", "fecha")
    date_hierarchy = "fecha"
    list_select_related = ("cliente", "empleado")
    inlines = [DetalleVentaInline]


@admin.register(DetalleVenta)
class DetalleVentaAdmin(admin.ModelAdmin):
    list_display = ("venta", "producto", "cantidad", "precio_unitario", "subtotal")
    search_fields = ("producto__nombre", "producto__codigo")
    list_select_related = ("venta", "producto")


@admin.register(RegistroProduccion)
class RegistroProduccionAdmin(admin.ModelAdmin):
    list_display = ("fecha", "turno", "material", "cantidad", "unidad", "supervisor")
    list_filter = ("material", "turno", "fecha")
    search_fields = ("observaciones",)
    date_hierarchy = "fecha"


# ==========================================================
# MODULOS AGREGADOS PARA EL PRODUCTO MINIMO VIABLE
# ==========================================================

from .models import (  # noqa: E402
    AccionMejora,
    Interaccion,
    ItemPedido,
    Oportunidad,
    Pedido,
    RegistroAcceso,
    RequisitoNormativo,
)


@admin.register(RegistroAcceso)
class RegistroAccesoAdmin(admin.ModelAdmin):
    """Solo lectura: una bitacora de seguridad que se puede editar no sirve
    como evidencia."""

    list_display = ("fecha", "nombre_usuario", "evento", "ip", "token_jti")
    list_filter = ("evento", "fecha")
    search_fields = ("nombre_usuario", "ip")
    date_hierarchy = "fecha"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False


@admin.register(Oportunidad)
class OportunidadAdmin(admin.ModelAdmin):
    list_display = ("titulo", "cliente", "etapa", "valor_estimado", "responsable", "fecha_cierre_estimada")
    list_filter = ("etapa",)
    search_fields = ("titulo", "cliente__nombre")
    list_select_related = ("cliente", "responsable")


@admin.register(Interaccion)
class InteraccionAdmin(admin.ModelAdmin):
    list_display = ("fecha", "cliente", "tipo", "descripcion", "registrado_por")
    list_filter = ("tipo",)
    search_fields = ("cliente__nombre", "descripcion")


class ItemPedidoInline(admin.TabularInline):
    model = ItemPedido
    extra = 0


@admin.register(Pedido)
class PedidoAdmin(admin.ModelAdmin):
    list_display = ("id", "cliente", "estado", "total", "metodo_pago", "creado", "pagado_en")
    list_filter = ("estado", "metodo_pago")
    search_fields = ("cliente__nombre", "referencia_pago")
    inlines = [ItemPedidoInline]


@admin.register(RequisitoNormativo)
class RequisitoNormativoAdmin(admin.ModelAdmin):
    list_display = ("nombre", "autoridad", "categoria", "estado", "fecha_vencimiento", "responsable")
    list_filter = ("autoridad", "categoria", "estado")
    search_fields = ("nombre", "norma")


@admin.register(AccionMejora)
class AccionMejoraAdmin(admin.ModelAdmin):
    list_display = ("titulo", "origen", "tipo", "fase", "responsable", "fecha_compromiso")
    list_filter = ("fase", "origen", "tipo")
    search_fields = ("titulo", "descripcion")
