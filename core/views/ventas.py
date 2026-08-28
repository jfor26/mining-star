"""
Registro y anulacion de ventas.

Es el modulo mas delicado del sistema: una venta toca tres tablas a la vez
(Venta, DetalleVenta y el stock de Producto). Si una de las tres falla y las
otras no, el inventario queda mintiendo.
"""

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import transaction
from django.db.models import F, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from ..forms import VentaRapidaForm
from ..models import DetalleVenta, Producto, Venta
from ._comunes import es_ajax, respuesta_error, respuesta_ok


class StockInsuficiente(Exception):
    """Se lanza dentro de la transaccion para deshacerla por completo."""


def _registrar_venta(cliente, producto, cantidad):
    """Crea la venta, su detalle y descuenta el stock, todo o nada.

    transaction.atomic() garantiza que si algo falla a mitad de camino,
    la base de datos vuelve exactamente al estado anterior. Antes no habia
    transaccion: si fallaba el descuento de stock, la venta quedaba
    registrada igual y el inventario descuadrado.
    """
    with transaction.atomic():
        venta = Venta.objects.create(cliente=cliente, total=0)

        DetalleVenta.objects.create(
            venta=venta,
            producto=producto,
            cantidad=cantidad,
            precio_unitario=producto.precio_venta,
            # el subtotal lo calcula DetalleVenta.save()
            subtotal=0,
        )

        # Descuento condicional en una sola instruccion SQL:
        #   UPDATE producto SET stock = stock - N WHERE id = X AND stock >= N
        # Si otro usuario vendio primero, la condicion no se cumple, update()
        # devuelve 0 y deshacemos todo. Esto cierra la ventana de tiempo
        # entre "leer el stock" y "guardarlo" que tenia el codigo anterior.
        filas = Producto.objects.filter(
            pk=producto.pk, stock__gte=cantidad
        ).update(stock=F("stock") - cantidad)

        if filas == 0:
            raise StockInsuficiente(producto.nombre)

        venta.recalcular_total()
        return venta


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

    with transaction.atomic():
        # Solo se devuelve el inventario si la venta seguia vigente.
        # Antes se devolvia siempre, asi que anular dos veces la misma
        # venta inflaba el stock con unidades inexistentes.
        if venta.estado != "Anulada":
            for detalle in venta.detalles.all():
                Producto.objects.filter(pk=detalle.producto_id).update(
                    stock=F("stock") + detalle.cantidad
                )

        venta.delete()

    messages.success(request, "Venta eliminada y stock devuelto al inventario.")
    return redirect("ventas")
