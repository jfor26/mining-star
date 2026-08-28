"""Tablero principal."""

from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import render

from ..forms import ClienteForm, EmpleadoForm, ProductoForm, ProveedorForm
from ..models import Cliente, Empleado, Producto, Proveedor, Venta


@login_required
def dashboard(request):
    # select_related trae el proveedor en la MISMA consulta.
    # Sin el, la plantilla dispara una consulta por cada producto
    # al pintar producto.proveedor (el problema N+1).
    productos = Producto.objects.select_related("proveedor")

    contexto = {
        "total_clientes": Cliente.objects.count(),
        "total_proveedores": Proveedor.objects.count(),
        "total_productos": productos.count(),
        "total_empleados": Empleado.objects.count(),
        "total_vendido": Venta.objects.aggregate(t=Sum("total"))["t"] or 0,

        # Formularios para los modales de creacion rapida del tablero.
        "form": EmpleadoForm(),
        "form_cliente": ClienteForm(),
        "form_producto": ProductoForm(),
        "form_proveedor": ProveedorForm(),

        "clientes": Cliente.objects.all(),
        "proveedores": Proveedor.objects.all(),
        "productos": productos,
    }
    return render(request, "dashboard/dashboard.html", contexto)
