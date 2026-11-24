"""
Asistente de Mining Star (chatbot por reglas, sin costo).

Responde preguntas frecuentes consultando la base de datos en el momento:
no inventa datos ni usa un servicio de inteligencia artificial externo.

Como funciona:
1. Normaliza la pregunta (minusculas, sin tildes).
2. La compara con una lista de intenciones; cada una tiene palabras clave y
   el modulo de la matriz de acceso que necesita el cargo para verla.
3. Si el cargo no tiene ese modulo, lo dice en lugar de mostrar el dato.
4. Cada respuesta indica de que modulo sale ("fuente"), para que el usuario
   pueda verificarla.

Esta separado en una funcion responder(usuario, pregunta) para poder cambiar
el motor mas adelante (por ejemplo, por un modelo de lenguaje) sin tocar la
API ni la pantalla.
"""

import re
import unicodedata
from datetime import timedelta

from django.db.models import F, Sum
from django.utils import timezone

from .models import Cliente, Oportunidad, Pqrs, Producto, RegistroProduccion, RequisitoNormativo, Venta
from .permisos import VER, puede
from .servicios import stock_materia_prima

SUGERENCIAS = [
    "¿Cuánto stock hay de caliza?",
    "¿Qué productos están en stock mínimo?",
    "¿Qué requisitos vencen pronto?",
    "¿Cuál fue la última venta?",
    "¿Cuánto se vendió este mes?",
    "¿Cuánto se produjo este mes?",
]

MATERIALES_PALABRAS = {"caliza": "Caliza", "marmol": "Marmol", "recebo": "Recebo"}


def normalizar(texto):
    sin_tildes = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9 ]", " ", sin_tildes.lower())


def _pesos(valor):
    return f"$ {valor:,.0f}".replace(",", ".")


def _cantidad(valor):
    texto = f"{valor:,.2f}".rstrip("0").rstrip(".")
    return texto.replace(",", "X").replace(".", ",").replace("X", ".")


def _r(texto, fuente):
    return {"respuesta": texto, "fuente": fuente}


# ---------- Intenciones ----------

def _stock(pregunta):
    partes = []
    material = next((m for palabra, m in MATERIALES_PALABRAS.items() if palabra in pregunta), None)
    if material:
        for fila in stock_materia_prima():
            if fila["material"] == material:
                partes.append(f"En la mina hay {_cantidad(fila['total'])} {fila['unidad']} de {fila['material_nombre'].lower()} como materia prima.")
    productos = [p for p in Producto.objects.all() if any(
        len(palabra) > 3 and palabra in normalizar(p.nombre) for palabra in pregunta.split()
        if palabra not in ("cuanto", "stock", "hay", "queda", "quedan", "inventario", "producto", "para")
    )]
    for p in productos[:5]:
        partes.append(f"«{p.nombre}» tiene {p.stock} unidades disponibles (mínimo {p.stock_minimo}).")
    if not partes:
        total = Producto.objects.aggregate(t=Sum("stock"))["t"] or 0
        partes.append(f"Hay {Producto.objects.count()} productos con {total} unidades en total. "
                      "Pregúnteme por uno en particular, por ejemplo «¿cuánto stock hay de recebo?».")
    return _r(" ".join(partes), "Producción e Inventario")


def _stock_minimo(_):
    bajos = list(Producto.objects.filter(stock__lte=F("stock_minimo")).order_by("stock"))
    if not bajos:
        return _r("Ningún producto está en stock mínimo.", "Inventario")
    lista = ", ".join(f"{p.nombre} ({p.stock})" for p in bajos)
    return _r(f"{len(bajos)} {'producto está' if len(bajos) == 1 else 'productos están'} en stock mínimo: {lista}.", "Inventario")


def _vencimientos(_):
    hoy = timezone.localdate()
    pendientes = RequisitoNormativo.objects.exclude(estado="Cumplido").filter(
        fecha_vencimiento__isnull=False, fecha_vencimiento__lte=hoy + timedelta(days=30)
    ).order_by("fecha_vencimiento")
    if not pendientes:
        return _r("No hay requisitos vencidos ni que venzan en los próximos 30 días.", "Normativa minera y ambiental")
    vencidos = [r for r in pendientes if r.fecha_vencimiento < hoy]
    proximos = [r for r in pendientes if r.fecha_vencimiento >= hoy]
    partes = []
    if vencidos:
        partes.append("Vencidos: " + "; ".join(f"{r.nombre} ante {r.autoridad} (desde el {r.fecha_vencimiento:%d/%m/%Y})" for r in vencidos) + ".")
    if proximos:
        partes.append("En los próximos 30 días: " + "; ".join(f"{r.nombre} ante {r.autoridad} el {r.fecha_vencimiento:%d/%m/%Y}" for r in proximos) + ".")
    return _r(" ".join(partes), "Normativa minera y ambiental")


def _ultima_venta(_):
    venta = Venta.objects.exclude(estado="Anulada").select_related("cliente").prefetch_related("detalles__producto").order_by("-fecha").first()
    if not venta:
        return _r("Todavía no hay ventas registradas.", "Ventas")
    productos = ", ".join(f"{d.producto.nombre} × {d.cantidad}" for d in venta.detalles.all())
    return _r(f"V-{venta.id:04d} del {timezone.localtime(venta.fecha):%d/%m/%Y} a {venta.cliente.nombre} por {_pesos(venta.total)}: {productos}.", "Ventas")


def _ventas_mes(_):
    inicio = timezone.localdate().replace(day=1)
    ventas = Venta.objects.exclude(estado="Anulada").filter(fecha__date__gte=inicio)
    total = ventas.aggregate(t=Sum("total"))["t"] or 0
    return _r(f"En {inicio:%m/%Y} van {ventas.count()} ventas por {_pesos(total)} (sin ventas anuladas).", "Ventas")


def _produccion_mes(_):
    inicio = timezone.localdate().replace(day=1)
    filas = (RegistroProduccion.objects.filter(fecha__gte=inicio).values("material", "unidad")
             .annotate(total=Sum("cantidad")).order_by("material"))
    if not filas:
        return _r("Este mes aún no hay registros de producción.", "Producción")
    nombres = dict(RegistroProduccion.MATERIALES)
    detalle = "; ".join(f"{nombres[f['material']].lower()}: {_cantidad(f['total'])} {f['unidad']}" for f in filas)
    return _r(f"Producción de {inicio:%m/%Y}: {detalle}.", "Producción")


def _cliente(pregunta):
    for cliente in Cliente.objects.all():
        nombre = normalizar(cliente.nombre)
        palabras = [p for p in nombre.split() if len(p) > 3 and p not in ("s a s", "sas", "ltda")]
        if palabras and sum(p in pregunta for p in palabras) >= min(2, len(palabras)):
            ventas = cliente.ventas.exclude(estado="Anulada")
            total = ventas.aggregate(t=Sum("total"))["t"] or 0
            abiertas = cliente.oportunidades.exclude(etapa__in=["Ganada", "Perdida"]).count()
            return _r(f"{cliente.nombre} (NIT/documento {cliente.documento}) tiene {ventas.count()} compras por {_pesos(total)} "
                      f"y {abiertas} {'oportunidad abierta' if abiertas == 1 else 'oportunidades abiertas'} en el CRM.", "Clientes y CRM")
    return None


def _pqrs(_):
    pendientes = Pqrs.objects.filter(estado__in=["Recibida", "EnTramite"]).order_by("creada")
    if not pendientes:
        return _r("No hay PQRS pendientes.", "Atención al cliente")
    lista = "; ".join(f"{q.radicado} ({q.get_tipo_display().lower()} de {q.nombre})" for q in pendientes[:5])
    return _r(f"Hay {pendientes.count()} PQRS sin responder: {lista}.", "Atención al cliente")


def _embudo(_):
    abiertas = Oportunidad.objects.exclude(etapa__in=["Ganada", "Perdida"])
    total = abiertas.aggregate(t=Sum("valor_estimado"))["t"] or 0
    return _r(f"Hay {abiertas.count()} oportunidades abiertas por {_pesos(total)} en el embudo comercial.", "CRM")


# (palabras clave, modulo requerido, funcion). Se evaluan en orden.
INTENCIONES = [
    (("minimo", "agotad", "bajo"), "productos", _stock_minimo),
    (("vence", "vencid", "requisito", "normativ", "anm", "cortolima"), "normativa", _vencimientos),
    (("ultima venta", "ultimo pedido", "venta mas reciente"), "ventas", _ultima_venta),
    (("vendio", "vendido", "ventas del mes", "ventas este mes", "cuanto se vende"), "ventas", _ventas_mes),
    (("produjo", "produccion", "extraj", "toneladas"), "produccion", _produccion_mes),
    (("pqrs", "queja", "reclamo", "peticion"), "pqrs", _pqrs),
    (("embudo", "oportunidad", "crm"), "crm", _embudo),
    (("stock", "inventario", "cuanto hay", "queda", "disponible"), "productos", _stock),
]


def responder(usuario, pregunta):
    texto = normalizar(pregunta or "").strip()
    if not texto:
        return {"respuesta": "Escriba una pregunta.", "fuente": None, "sugerencias": SUGERENCIAS}
    if texto in ("hola", "buenas", "buenos dias", "buenas tardes", "ayuda", "que puedes hacer"):
        nombre = usuario.first_name or usuario.username
        return {"respuesta": f"Hola, {nombre}. Puedo consultar inventario, producción, ventas, clientes, normativa y PQRS. "
                             "Pruebe con una de las sugerencias.", "fuente": None, "sugerencias": SUGERENCIAS}

    for palabras, modulo, funcion in INTENCIONES:
        if any(p in texto for p in palabras):
            if not puede(usuario, modulo, VER):
                return {"respuesta": "Su cargo no tiene acceso a esa información.", "fuente": None, "sugerencias": SUGERENCIAS}
            resultado = funcion(texto)
            return {**resultado, "sugerencias": SUGERENCIAS}

    if puede(usuario, "clientes", VER):
        resultado = _cliente(texto)
        if resultado:
            return {**resultado, "sugerencias": SUGERENCIAS}

    return {
        "respuesta": "No entendí la pregunta. Puedo responder sobre stock, stock mínimo, ventas, producción, "
                     "requisitos normativos, clientes, CRM y PQRS. Pruebe con una sugerencia.",
        "fuente": None,
        "sugerencias": SUGERENCIAS,
    }
