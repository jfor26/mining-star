"""Pagina de reportes: reune en un solo lugar las exportaciones del sistema.

Cada modulo ya generaba su reporte en Excel y en PDF, pero solo se podia
llegar a el desde la pantalla del modulo. El enlace "Reportes" del menu
apuntaba a "#".
"""

from django.contrib.auth.decorators import login_required
from django.shortcuts import render

from ..models import Cliente, Empleado, Producto, Proveedor, RegistroProduccion, Venta

REPORTES = [
    # (titulo, icono, modelo, url Excel, url PDF, url de la pantalla)
    ("Empleados", "fa-user-tie", Empleado, "exportar_empleados_excel", "exportar_empleados_pdf", "empleados"),
    ("Clientes", "fa-users", Cliente, "exportar_clientes_excel", "exportar_clientes_pdf", "clientes"),
    ("Productos e inventario", "fa-box-open", Producto, "exportar_productos_excel", "exportar_productos_pdf", "productos"),
    ("Proveedores", "fa-truck-fast", Proveedor, "exportar_proveedores_excel", "exportar_proveedores_pdf", "proveedores"),
]


@login_required
def reportes(request):
    tarjetas = [
        {"titulo": t, "icono": i, "total": m.objects.count(), "excel": x, "pdf": p, "pantalla": v}
        for t, i, m, x, p, v in REPORTES
    ]
    return render(request, "reportes/reportes.html", {
        "tarjetas": tarjetas,
        "total_ventas": Venta.objects.count(),
        "total_produccion": RegistroProduccion.objects.count(),
    })
