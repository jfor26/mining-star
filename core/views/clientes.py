"""CRUD y reportes de clientes."""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..exportadores import Columna, exportar_excel, exportar_pdf
from ..forms import ClienteForm
from ..models import Cliente
from ._comunes import es_ajax, respuesta_error, respuesta_ok

COLUMNAS = [
    Columna("Documento", lambda c: c.documento, 80),
    Columna("Nombre", lambda c: c.nombre, 140, izquierda=True),
    Columna("Empresa", lambda c: c.empresa, 130, izquierda=True),
    Columna("Correo", lambda c: c.correo, 150, izquierda=True),
    Columna("Teléfono", lambda c: c.telefono, 90),
]


@login_required
def clientes(request):
    if request.method == "POST":
        # ANTES: Cliente.objects.create(documento=request.POST.get(...), ...)
        # Eso escribia en la base de datos SIN validar nada: un documento
        # repetido reventaba con IntegrityError (error 500) y un campo
        # ausente entraba como None.
        formulario = ClienteForm(request.POST)

        if formulario.is_valid():
            formulario.save()
            if es_ajax(request):
                return respuesta_ok("Cliente agregado correctamente.")
            messages.success(request, "Cliente agregado correctamente.")
            return redirect("clientes")

        if es_ajax(request):
            return respuesta_error(formulario.errors)
        messages.error(request, "Revisa los datos del formulario.")
    else:
        formulario = ClienteForm()

    lista = Cliente.objects.all()
    return render(request, "clientes/clientes.html", {
        "form": formulario,
        "clientes": lista,
        "total_clientes": lista.count(),
    })


@login_required
def editar_cliente(request, id):
    cliente = get_object_or_404(Cliente, pk=id)

    if request.method == "POST":
        formulario = ClienteForm(request.POST, instance=cliente)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Cliente actualizado correctamente.")
            return redirect("clientes")
        messages.error(request, "Revisa los datos del formulario.")
    else:
        formulario = ClienteForm(instance=cliente)

    return render(request, "clientes/editar_cliente.html", {
        "form": formulario,
        "cliente": cliente,
    })


@login_required
@require_POST
def eliminar_cliente(request, id):
    # @require_POST rechaza los GET. Antes bastaba con abrir la URL
    # /clientes/eliminar/3/ para borrar: un rastreador, el prefetch del
    # navegador o un enlace compartido borraban datos sin confirmacion.
    cliente = get_object_or_404(Cliente, pk=id)
    try:
        cliente.delete()
        messages.success(request, "Cliente eliminado correctamente.")
    except ProtectedError:
        messages.error(
            request,
            "No se puede eliminar: el cliente tiene ventas registradas.",
        )
    return redirect("clientes")


@login_required
def exportar_clientes_excel(request):
    return exportar_excel(Cliente.objects.all(), COLUMNAS, "Clientes", "Clientes")


@login_required
def exportar_clientes_pdf(request):
    return exportar_pdf(Cliente.objects.all(), COLUMNAS, "Listado de Clientes", "Clientes")
