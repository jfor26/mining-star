"""
Paquete de vistas de Mining Star.

core/views.py tenia 2.566 lineas con todo mezclado. Ahora cada dominio vive
en su propio modulo y este archivo los reexporta, de modo que core/urls.py
sigue escribiendo "views.clientes" sin enterarse del cambio.
"""

from .autenticacion import login_view, logout_view
from .clientes import (
    clientes,
    editar_cliente,
    eliminar_cliente,
    exportar_clientes_excel,
    exportar_clientes_pdf,
)
from .empleados import (
    editar_empleado,
    eliminar_empleado,
    empleados,
    exportar_empleados_excel,
    exportar_empleados_pdf,
)
from .panel import dashboard
from .productos import (
    editar_producto,
    eliminar_producto,
    exportar_productos_excel,
    exportar_productos_pdf,
    nuevo_producto,
    productos,
)
from .proveedores import (
    editar_proveedor,
    eliminar_proveedor,
    exportar_proveedores_excel,
    exportar_proveedores_pdf,
    proveedores,
)
from .ventas import eliminar_venta, ventas

__all__ = [
    "login_view", "logout_view", "dashboard",
    "clientes", "editar_cliente", "eliminar_cliente",
    "exportar_clientes_excel", "exportar_clientes_pdf",
    "empleados", "editar_empleado", "eliminar_empleado",
    "exportar_empleados_excel", "exportar_empleados_pdf",
    "productos", "nuevo_producto", "editar_producto", "eliminar_producto",
    "exportar_productos_excel", "exportar_productos_pdf",
    "proveedores", "editar_proveedor", "eliminar_proveedor",
    "exportar_proveedores_excel", "exportar_proveedores_pdf",
    "ventas", "eliminar_venta",
]
