"""Tablero principal."""

import json
from decimal import Decimal

from django.contrib.auth.decorators import login_required
from django.db.models import F, Sum
from django.db.models.functions import ExtractMonth
from django.shortcuts import render
from django.utils import timezone

from ..forms import ClienteForm, EmpleadoForm, ProductoForm, ProveedorForm
from ..models import Cliente, Empleado, Producto, Proveedor, Venta


@login_required
def dashboard(request):
    # select_related trae el proveedor en la MISMA consulta.
    # Sin el, la plantilla dispara una consulta por cada producto
    # al pintar producto.proveedor (el problema N+1).
    productos = Producto.objects.select_related("proveedor")

    # Subtitulos reales de cada tarjeta: en vez de textos fijos como
    # "+12 este mes", cada tarjeta resume un hecho verdadero de la base.
    empleados_activos = Empleado.objects.filter(estado="Activo").count()
    proveedores_activos = Proveedor.objects.count()
    # stock_bajo es una propiedad de Python; el filtro equivalente en la
    # base es stock <= stock_minimo.
    productos_stock_bajo = Producto.objects.filter(
        stock__lte=F("stock_minimo")
    ).count()
    total_ventas = Venta.objects.count()

    # Ventas por mes del año en curso, para el grafico de barras. Antes el
    # grafico traia una serie fija; ahora se arma con lo que hay en la base.
    anio = timezone.localdate().year
    por_mes = dict(
        Venta.objects.filter(fecha__year=anio)
        .annotate(mes=ExtractMonth("fecha"))
        .values("mes")
        .annotate(total=Sum("total"))
        .values_list("mes", "total")
    )
    ventas_por_mes = [float(por_mes.get(m, 0) or 0) for m in range(1, 13)]

    contexto = {
        "total_clientes": Cliente.objects.count(),
        "total_proveedores": Proveedor.objects.count(),
        "total_productos": productos.count(),
        "total_empleados": Empleado.objects.count(),
        "total_vendido": Venta.objects.aggregate(t=Sum("total"))["t"] or Decimal("0"),

        # Datos derivados para los subtitulos de las tarjetas.
        "empleados_activos": empleados_activos,
        "proveedores_activos": proveedores_activos,
        "productos_stock_bajo": productos_stock_bajo,
        "total_ventas": total_ventas,
        "ventas_por_mes_json": json.dumps(ventas_por_mes),

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
