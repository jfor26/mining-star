"""CRUD y reportes de productos."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F, ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..exportadores import Columna, exportar_excel, exportar_pdf
from ..forms import ProductoForm
from ..models import Producto
from ._comunes import es_ajax, respuesta_error, respuesta_ok

COLUMNAS = [
    Columna("Código", lambda p: p.codigo, 70),
    Columna("Nombre", lambda p: p.nombre, 130, izquierda=True),
    Columna("Categoría", lambda p: p.categoria, 90, izquierda=True),
    Columna("Proveedor", lambda p: p.proveedor.empresa, 110, izquierda=True),
    Columna("P. compra", lambda p: p.precio_compra, 70),
    Columna("P. venta", lambda p: p.precio_venta, 70),
    Columna("Stock", lambda p: p.stock, 50),
]


def _consulta_base():
    # select_related evita una consulta extra por producto al leer
    # p.proveedor.empresa en la plantilla o en el reporte.
    return Producto.objects.select_related("proveedor")


@login_required
def productos(request):
    lista = _consulta_base()
    return render(request, "productos/productos.html", {
        "productos": lista,
        "total_productos": lista.count(),
        "productos_stock_bajo": lista.filter(stock__lte=F("stock_minimo")).count(),
    })


@login_required
def nuevo_producto(request):
    if request.method == "POST":
        formulario = ProductoForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            if es_ajax(request):
                return respuesta_ok("Producto registrado correctamente.")
            messages.success(request, "Producto registrado correctamente.")
            return redirect("productos")

        if es_ajax(request):
            return respuesta_error(formulario.errors)
        messages.error(request, "Revisa los datos del formulario.")
    else:
        formulario = ProductoForm()

    return render(request, "productos/nuevo_producto.html", {
        "form": formulario,
        "proveedores": formulario.fields["proveedor"].queryset,
    })


@login_required
def editar_producto(request, id):
    producto = get_object_or_404(_consulta_base(), pk=id)

    if request.method == "POST":
        formulario = ProductoForm(request.POST, instance=producto)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Producto actualizado correctamente.")
            return redirect("productos")
        messages.error(request, "Revisa los datos del formulario.")
    else:
        formulario = ProductoForm(instance=producto)

    return render(request, "productos/editar_producto.html", {
        "form": formulario,
        "producto": producto,
        "proveedores": formulario.fields["proveedor"].queryset,
    })


@login_required
@require_POST
def eliminar_producto(request, id):
    producto = get_object_or_404(Producto, pk=id)
    try:
        producto.delete()
        messages.success(request, "Producto eliminado correctamente.")
    except ProtectedError:
        messages.error(
            request,
            "No se puede eliminar: el producto aparece en ventas registradas.",
        )
    return redirect("productos")


@login_required
def exportar_productos_excel(request):
    return exportar_excel(_consulta_base(), COLUMNAS, "Productos", "Productos")


@login_required
def exportar_productos_pdf(request):
    return exportar_pdf(
        _consulta_base(), COLUMNAS, "Listado de Productos", "Productos"
    )
