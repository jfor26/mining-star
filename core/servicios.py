"""
Servicios de dominio de Mining Star.

Aqui vive la logica de negocio que NO depende de como llegue la peticion.
La razon es concreta: el registro de una venta toca tres tablas a la vez
(Venta, DetalleVenta y el stock de Producto) y esa operacion tiene que ser
identica se invoque desde el formulario web o desde la API REST.

Duplicar ese codigo en dos sitios seria la forma mas rapida de que un dia
la web descuente el inventario y la API no, o al reves.
"""

from decimal import Decimal

from django.db import transaction
from django.db.models import F

from .models import DetalleVenta, Producto, Venta


class StockInsuficiente(Exception):
    """Se lanza dentro de la transaccion para deshacerla por completo.

    Lleva el nombre del producto para que quien la capture pueda construir
    un mensaje util sin volver a consultar la base de datos.
    """

    def __init__(self, producto):
        self.producto = producto
        super().__init__(f"Stock insuficiente para {producto}")


@transaction.atomic
def registrar_venta(cliente, producto, cantidad, empleado=None):
    """Crea la venta, su detalle y descuenta el stock: todo o nada.

    transaction.atomic garantiza que si algo falla a mitad de camino la base
    de datos vuelve exactamente al estado anterior. Antes no habia
    transaccion: si fallaba el descuento de stock, la venta quedaba
    registrada igual y el inventario descuadrado.

    Devuelve la venta creada. Lanza StockInsuficiente si no hay existencias.
    """
    venta = Venta.objects.create(cliente=cliente, empleado=empleado, total=0)

    DetalleVenta.objects.create(
        venta=venta,
        producto=producto,
        cantidad=cantidad,
        precio_unitario=producto.precio_venta,
        subtotal=0,  # lo calcula DetalleVenta.save()
    )

    # Descuento condicional en una sola instruccion SQL:
    #   UPDATE producto SET stock = stock - N WHERE id = X AND stock >= N
    # Si otro usuario vendio primero, la condicion no se cumple, update()
    # devuelve 0 y deshacemos todo. Esto cierra la ventana de tiempo entre
    # "leer el stock" y "guardarlo" que tenia el codigo anterior.
    filas = Producto.objects.filter(
        pk=producto.pk, stock__gte=cantidad
    ).update(stock=F("stock") - cantidad)

    if filas == 0:
        raise StockInsuficiente(producto.nombre)

    venta.recalcular_total()
    return venta


@transaction.atomic
def anular_venta(venta):
    """Devuelve el inventario de una venta y la marca como anulada.

    Solo se devuelve el stock si la venta seguia vigente. Anular dos veces
    la misma venta inflaria el inventario con unidades inexistentes.
    """
    if venta.estado == "Anulada":
        return venta

    for detalle in venta.detalles.all():
        Producto.objects.filter(pk=detalle.producto_id).update(
            stock=F("stock") + detalle.cantidad
        )

    venta.estado = "Anulada"
    venta.save(update_fields=["estado"])
    return venta


@transaction.atomic
def eliminar_venta(venta):
    """Devuelve el inventario y borra la venta del registro."""
    if venta.estado != "Anulada":
        for detalle in venta.detalles.all():
            Producto.objects.filter(pk=detalle.producto_id).update(
                stock=F("stock") + detalle.cantidad
            )
    venta.delete()


def total_vendido():
    """Suma el total de todas las ventas no anuladas."""
    from django.db.models import Sum

    agregado = Venta.objects.exclude(estado="Anulada").aggregate(t=Sum("total"))
    return agregado["t"] or Decimal("0")
