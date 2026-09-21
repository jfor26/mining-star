"""
Registro y anulacion de ventas.

Es el modulo mas delicado del sistema: una venta toca tres tablas a la vez
(Venta, DetalleVenta y el stock de Producto). Si una de las tres falla y las
otras no, el inventario queda mintiendo.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..forms import VentaRapidaForm
from ..models import Venta
from ..servicios import StockInsuficiente
from ..servicios import eliminar_venta as _eliminar_venta
from ..servicios import registrar_venta as _registrar_venta
from ._comunes import es_ajax, respuesta_error, respuesta_ok

# La logica de registro y anulacion vive en core/servicios.py porque la
# comparten esta vista y la API REST. Duplicarla seria la forma mas rapida
# de que un dia la web descuente inventario y la API no.


@login_required
def ventas(request):
    if request.method == "POST":
        formulario = VentaRapidaForm(request.POST)

        if formulario.is_valid():
            datos = formulario.cleaned_data
            try:
                _registrar_venta(
                    datos["cliente"], datos["producto"], datos["cantidad"]
                )
            except StockInsuficiente:
                mensaje = "Stock insuficiente: otro usuario acaba de vender ese producto."
                if es_ajax(request):
                    return respuesta_error({"cantidad": [mensaje]})
                messages.error(request, mensaje)
                return redirect("ventas")

            if es_ajax(request):
                return respuesta_ok("Venta registrada correctamente.")
            messages.success(request, "Venta registrada correctamente.")
            return redirect("ventas")

        if es_ajax(request):
            return respuesta_error(formulario.errors)
        messages.error(request, "Revisa los datos de la venta.")
    else:
        formulario = VentaRapidaForm()

    listado = (
        Venta.objects
        .select_related("cliente", "empleado")
        .prefetch_related("detalles__producto")[:20]
    )

    return render(request, "ventas/ventas.html", {
        "form": formulario,
        "clientes": formulario.fields["cliente"].queryset,
        "productos": formulario.fields["producto"].queryset,
        "ventas": listado,
        "total_vendido": Venta.objects.aggregate(t=Sum("total"))["t"] or 0,
    })


@login_required
@require_POST
def eliminar_venta(request, id):
    # BUG ORIGINAL: esta funcion no terminaba con un return, asi que Django
    # lanzaba "The view didn't return an HttpResponse object" (error 500)
    # cada vez que se eliminaba una venta.
    venta = get_object_or_404(
        Venta.objects.prefetch_related("detalles"), pk=id
    )

    # Solo se devuelve el inventario si la venta seguia vigente. Antes se
    # devolvia siempre, asi que anular dos veces la misma venta inflaba el
    # stock con unidades inexistentes.
    _eliminar_venta(venta)

    messages.success(request, "Venta eliminada y stock devuelto al inventario.")
    return redirect("ventas")
