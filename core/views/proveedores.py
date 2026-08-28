"""CRUD y reportes de proveedores."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..exportadores import Columna, exportar_excel, exportar_pdf
from ..forms import ProveedorForm
from ..models import Proveedor
from ._comunes import es_ajax, respuesta_error, respuesta_ok

COLUMNAS = [
    Columna("NIT", lambda p: p.nit, 80),
    Columna("Empresa", lambda p: p.empresa, 130, izquierda=True),
    Columna("Contacto", lambda p: p.contacto, 120, izquierda=True),
    Columna("Correo", lambda p: p.correo, 140, izquierda=True),
    Columna("Teléfono", lambda p: p.telefono, 80),
    Columna("Ciudad", lambda p: p.ciudad, 80),
]


@login_required
def proveedores(request):
    if request.method == "POST":
        formulario = ProveedorForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            if es_ajax(request):
                return respuesta_ok("Proveedor agregado correctamente.")
            messages.success(request, "Proveedor agregado correctamente.")
            return redirect("proveedores")

        if es_ajax(request):
            return respuesta_error(formulario.errors)
        messages.error(request, "Revisa los datos del formulario.")
    else:
        formulario = ProveedorForm()

    lista = Proveedor.objects.all()
    return render(request, "proveedores/proveedores.html", {
        "form": formulario,
        "proveedores": lista,
        "total_proveedores": lista.count(),
    })


@login_required
def editar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, pk=id)

    if request.method == "POST":
        formulario = ProveedorForm(request.POST, instance=proveedor)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Proveedor actualizado correctamente.")
            return redirect("proveedores")
        messages.error(request, "Revisa los datos del formulario.")
    else:
        formulario = ProveedorForm(instance=proveedor)

    return render(request, "proveedores/editar_proveedor.html", {
        "form": formulario,
        "proveedor": proveedor,
    })


@login_required
@require_POST
def eliminar_proveedor(request, id):
    proveedor = get_object_or_404(Proveedor, pk=id)
    try:
        proveedor.delete()
        messages.success(request, "Proveedor eliminado correctamente.")
    except ProtectedError:
        messages.error(
            request,
            "No se puede eliminar: el proveedor tiene productos asociados.",
        )
    return redirect("proveedores")


@login_required
def exportar_proveedores_excel(request):
    return exportar_excel(
        Proveedor.objects.all(), COLUMNAS, "Proveedores", "Proveedores"
    )


@login_required
def exportar_proveedores_pdf(request):
    return exportar_pdf(
        Proveedor.objects.all(), COLUMNAS, "Listado de Proveedores", "Proveedores"
    )
