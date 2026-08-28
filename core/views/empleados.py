"""CRUD y reportes de empleados."""

from datetime import timedelta

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from ..exportadores import Columna, exportar_excel, exportar_pdf
from ..forms import EmpleadoForm
from ..models import Empleado
from ._comunes import es_ajax, respuesta_error, respuesta_ok

COLUMNAS = [
    Columna("Documento", lambda e: e.documento, 75),
    Columna("Nombre", lambda e: e.nombre_completo, 120, izquierda=True),
    Columna("Cargo", lambda e: e.cargo, 80, izquierda=True),
    Columna("Área", lambda e: e.area, 90, izquierda=True),
    Columna("Correo", lambda e: e.correo, 130, izquierda=True),
    Columna("Teléfono", lambda e: e.telefono, 70),
    Columna("Estado", lambda e: e.estado, 65),
]


@login_required
def empleados(request):
    if request.method == "POST":
        formulario = EmpleadoForm(request.POST)
        if formulario.is_valid():
            formulario.save()
            if es_ajax(request):
                return respuesta_ok("Empleado agregado correctamente.")
            messages.success(request, "Empleado agregado correctamente.")
            return redirect("empleados")

        if es_ajax(request):
            return respuesta_error(formulario.errors)
        messages.error(request, "Revisa los datos del formulario.")
    else:
        formulario = EmpleadoForm()

    lista = Empleado.objects.all()

    # "Nuevos" antes devolvia lista.count(), es decir el total: siempre
    # mostraba el mismo numero que la tarjeta de al lado. Ahora cuenta
    # de verdad los que ingresaron en los ultimos 30 dias.
    hace_30_dias = timezone.localdate() - timedelta(days=30)

    return render(request, "empleados/empleados.html", {
        "form": formulario,
        "empleados": lista,
        "total_empleados": lista.count(),
        "empleados_activos": lista.filter(estado="Activo").count(),
        "empleados_vacaciones": lista.filter(estado="Vacaciones").count(),
        "empleados_nuevos": lista.filter(fecha_ingreso__gte=hace_30_dias).count(),
    })


@login_required
def editar_empleado(request, id):
    empleado = get_object_or_404(Empleado, pk=id)

    if request.method == "POST":
        formulario = EmpleadoForm(request.POST, instance=empleado)
        if formulario.is_valid():
            formulario.save()
            messages.success(request, "Empleado actualizado correctamente.")
            return redirect("empleados")
        messages.error(request, "Revisa los datos del formulario.")
    else:
        formulario = EmpleadoForm(instance=empleado)

    return render(request, "empleados/editar_empleado.html", {
        "form": formulario,
        "empleado": empleado,
    })


@login_required
@require_POST
def eliminar_empleado(request, id):
    empleado = get_object_or_404(Empleado, pk=id)
    try:
        empleado.delete()
        messages.success(request, "Empleado eliminado correctamente.")
    except ProtectedError:
        messages.error(
            request,
            "No se puede eliminar: el empleado tiene ventas registradas.",
        )
    return redirect("empleados")


@login_required
def exportar_empleados_excel(request):
    return exportar_excel(Empleado.objects.all(), COLUMNAS, "Empleados", "Empleados")


@login_required
def exportar_empleados_pdf(request):
    return exportar_pdf(
        Empleado.objects.all(), COLUMNAS, "Listado de Empleados", "Empleados"
    )
