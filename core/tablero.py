"""
Calculos del dashboard de Mining Star.

Cada funcion devuelve una serie lista para graficar (lista de diccionarios).
Las agregaciones se hacen en la base de datos (annotate/aggregate) y no en
Python: con miles de ventas, traer todas las filas para sumarlas aqui seria
lento e innecesario.
"""

from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, DecimalField, ExpressionWrapper, F, Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone

from .models import (
    AccionMejora,
    Cliente,
    DetalleVenta,
    Empleado,
    Oportunidad,
    Pedido,
    Producto,
    RegistroAcceso,
    RegistroProduccion,
    RequisitoNormativo,
    Venta,
)

MESES = ["ene", "feb", "mar", "abr", "may", "jun", "jul", "ago", "sep", "oct", "nov", "dic"]


def _meses_atras(n):
    """Primer dia de cada uno de los ultimos n meses, del mas antiguo al actual."""
    hoy = timezone.localdate().replace(day=1)
    meses = []
    anio, mes = hoy.year, hoy.month
    for _ in range(n):
        meses.append(hoy.replace(year=anio, month=mes))
        mes -= 1
        if mes == 0:
            anio, mes = anio - 1, 12
    return list(reversed(meses))


def ventas_por_mes(meses=6):
    inicio = _meses_atras(meses)[0]
    filas = (
        Venta.objects.exclude(estado="Anulada")
        .filter(fecha__date__gte=inicio)
        .annotate(mes=TruncMonth("fecha"))
        .values("mes")
        .annotate(total=Sum("total"), cantidad=Count("id"))
    )
    por_mes = {(f["mes"].year, f["mes"].month): f for f in filas}
    salida = []
    for m in _meses_atras(meses):
        f = por_mes.get((m.year, m.month), {})
        salida.append({
            "mes": f"{MESES[m.month - 1]} {m.year % 100:02d}",
            "total": float(f.get("total") or 0),
            "ventas": f.get("cantidad", 0),
        })
    return salida


def top_productos(limite=5):
    filas = (
        DetalleVenta.objects.exclude(venta__estado="Anulada")
        .values("producto__nombre")
        .annotate(unidades=Sum("cantidad"), ingresos=Sum("subtotal"))
        .order_by("-ingresos")[:limite]
    )
    return [
        {"producto": f["producto__nombre"], "unidades": f["unidades"], "ingresos": float(f["ingresos"])}
        for f in filas
    ]


def inventario_por_categoria():
    valor = ExpressionWrapper(F("stock") * F("precio_venta"), output_field=DecimalField())
    filas = (
        Producto.objects.values("categoria")
        .annotate(unidades=Sum("stock"), valor=Sum(valor), productos=Count("id"))
        .order_by("-valor")
    )
    return [
        {"categoria": f["categoria"], "unidades": f["unidades"] or 0,
         "valor": float(f["valor"] or 0), "productos": f["productos"]}
        for f in filas
    ]


def produccion_por_material(dias=30):
    desde = timezone.localdate() - timedelta(days=dias)
    nombres = dict(RegistroProduccion.MATERIALES)
    filas = (
        RegistroProduccion.objects.filter(fecha__gte=desde)
        .values("material", "unidad")
        .annotate(total=Sum("cantidad"))
        .order_by("material")
    )
    return [
        {"material": nombres[f["material"]], "unidad": f["unidad"], "total": float(f["total"])}
        for f in filas
    ]


def produccion_diaria(dias=14):
    """Toneladas por dia y por material (solo registros en toneladas)."""
    hoy = timezone.localdate()
    desde = hoy - timedelta(days=dias - 1)
    filas = (
        RegistroProduccion.objects.filter(fecha__gte=desde, unidad="t")
        .values("fecha", "material")
        .annotate(total=Sum("cantidad"))
    )
    serie = {desde + timedelta(days=i): {"Marmol": 0, "Caliza": 0, "Recebo": 0} for i in range(dias)}
    for f in filas:
        serie[f["fecha"]][f["material"]] = float(f["total"])
    return [{"dia": d.strftime("%d/%m"), **valores} for d, valores in serie.items()]


def embudo_crm():
    nombres = dict(Oportunidad.ETAPAS)
    filas = {
        f["etapa"]: f
        for f in Oportunidad.objects.values("etapa").annotate(cantidad=Count("id"), valor=Sum("valor_estimado"))
    }
    return [
        {"etapa": nombres[e], "clave": e, "cantidad": filas.get(e, {}).get("cantidad", 0),
         "valor": float(filas.get(e, {}).get("valor") or 0)}
        for e, _ in Oportunidad.ETAPAS
    ]


def conteo_por(modelo, campo, opciones):
    nombres = dict(opciones)
    filas = {f[campo]: f["n"] for f in modelo.objects.values(campo).annotate(n=Count("id"))}
    return [{"clave": k, "nombre": nombres[k], "cantidad": filas.get(k, 0)} for k, _ in opciones]


def proximos_vencimientos(limite=5):
    hoy = timezone.localdate()
    consulta = (
        RequisitoNormativo.objects.exclude(estado="Cumplido")
        .filter(fecha_vencimiento__isnull=False)
        .order_by("fecha_vencimiento")[:limite]
    )
    return [
        {"id": r.id, "nombre": r.nombre, "autoridad": r.autoridad,
         "fecha_vencimiento": r.fecha_vencimiento.isoformat(),
         "dias": (r.fecha_vencimiento - hoy).days, "alerta": r.alerta}
        for r in consulta
    ]


def accesos_recientes(dias=7):
    hoy = timezone.localdate()
    desde = hoy - timedelta(days=dias - 1)
    filas = (
        RegistroAcceso.objects.filter(fecha__date__gte=desde)
        .annotate(dia=TruncDate("fecha"))
        .values("dia", "evento")
        .annotate(n=Count("id"))
    )
    serie = {desde + timedelta(days=i): {"ingresos": 0, "fallidos": 0} for i in range(dias)}
    for f in filas:
        if f["dia"] in serie:
            if f["evento"] == "ingreso":
                serie[f["dia"]]["ingresos"] += f["n"]
            elif f["evento"] in ("fallido", "bloqueado"):
                serie[f["dia"]]["fallidos"] += f["n"]
    return [{"dia": d.strftime("%d/%m"), **v} for d, v in serie.items()]


def construir_dashboard(visibles):
    """Arma la respuesta del dashboard con los bloques que el cargo puede ver."""
    datos = {"indicadores": {}}
    ind = datos["indicadores"]

    if "ventas" in visibles:
        vigentes = Venta.objects.exclude(estado="Anulada")
        ind["total_vendido"] = float(vigentes.aggregate(t=Sum("total"))["t"] or Decimal("0"))
        ind["ventas"] = vigentes.count()
        datos["ventas_por_mes"] = ventas_por_mes()
        datos["top_productos"] = top_productos()
    if "productos" in visibles:
        ind["productos"] = Producto.objects.count()
        ind["stock_bajo"] = Producto.objects.filter(stock__lte=F("stock_minimo")).count()
        datos["inventario_por_categoria"] = inventario_por_categoria()
    if "clientes" in visibles:
        ind["clientes"] = Cliente.objects.count()
    if "empleados" in visibles:
        ind["empleados"] = Empleado.objects.filter(estado="Activo").count()
    if "produccion" in visibles:
        datos["produccion_por_material"] = produccion_por_material()
        datos["produccion_diaria"] = produccion_diaria()
        ind["toneladas_mes"] = float(
            RegistroProduccion.objects.filter(
                unidad="t", fecha__gte=timezone.localdate().replace(day=1)
            ).aggregate(t=Sum("cantidad"))["t"] or 0
        )
    if "crm" in visibles:
        datos["embudo_crm"] = embudo_crm()
        abiertas = Oportunidad.objects.exclude(etapa__in=["Ganada", "Perdida"])
        ind["oportunidades_abiertas"] = abiertas.count()
        ind["valor_embudo"] = float(abiertas.aggregate(v=Sum("valor_estimado"))["v"] or 0)
    if "pedidos" in visibles:
        datos["pedidos_por_estado"] = conteo_por(Pedido, "estado", Pedido.ESTADOS)
    if "normativa" in visibles:
        datos["normativa_por_estado"] = conteo_por(RequisitoNormativo, "estado", RequisitoNormativo.ESTADOS)
        datos["proximos_vencimientos"] = proximos_vencimientos()
        total = RequisitoNormativo.objects.count()
        cumplidos = RequisitoNormativo.objects.filter(estado="Cumplido").count()
        ind["cumplimiento_normativo"] = round(100 * cumplidos / total) if total else 0
    if "mejora" in visibles:
        datos["mejora_por_fase"] = conteo_por(AccionMejora, "fase", AccionMejora.FASES)
    if "seguridad" in visibles:
        datos["accesos_recientes"] = accesos_recientes()
    return datos
