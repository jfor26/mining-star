"""
Produccion diaria de la mina (historia de usuario HU-001).

El supervisor registra por turno el material extraido. La pantalla muestra
ademas el stock acumulado de materia prima y el reporte del dia elegido,
que son los otros dos criterios de aceptacion de la historia.
"""

from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..forms import ProduccionForm
from ..models import RegistroProduccion
from ..servicios import reporte_diario, stock_materia_prima


def _fecha_consultada(request):
    """Fecha del reporte: la de ?fecha=AAAA-MM-DD o, si falta o es invalida, hoy."""
    try:
        return date.fromisoformat(request.GET.get("fecha", ""))
    except ValueError:
        return date.today()


@login_required
def produccion(request):
    if request.method == "POST":
        formulario = ProduccionForm(request.POST)
        if formulario.is_valid():
            registro = formulario.save(commit=False)
            registro.registrado_por = request.user
            registro.save()
            messages.success(request, f"Producción registrada: {registro}.")
            return redirect(f"{request.path}?fecha={registro.fecha.isoformat()}")
        messages.error(request, "Revisa los datos del registro de producción.")
    else:
        formulario = ProduccionForm()

    fecha = _fecha_consultada(request)
    registros_dia, totales_dia = reporte_diario(fecha)

    return render(request, "produccion/produccion.html", {
        "form": formulario,
        # Si el formulario llego con errores, el modal se vuelve a abrir
        # para que el supervisor vea que corregir sin perder lo digitado.
        "abrir_modal": request.method == "POST",
        "fecha": fecha,
        "registros_dia": registros_dia,
        "totales_dia": totales_dia,
        "stock": stock_materia_prima(),
        "recientes": RegistroProduccion.objects.select_related("supervisor")[:15],
    })


@login_required
@require_POST
def eliminar_produccion(request, id):
    registro = get_object_or_404(RegistroProduccion, pk=id)
    descripcion = str(registro)
    registro.delete()
    messages.success(request, f"Registro eliminado: {descripcion}.")
    return redirect("produccion")
