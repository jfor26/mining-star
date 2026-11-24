"""
Avisos de la campana de notificaciones.

Se calculan al consultar, desde el estado real del sistema, y cada cargo
recibe solo los de los modulos que puede ver (matriz de core/permisos.py):

- inventario  (productos): productos con stock en el minimo o por debajo;
- normativa   (normativa): requisitos vencidos o que vencen en 30 dias o menos;
- tienda      (pedidos):   pedidos pagados en los ultimos 7 dias;
- crm         (crm):       oportunidades abiertas con 7 dias o mas sin contacto;
- pqrs        (pqrs):      PQRS sin responder y mensajes de contacto sin atender.

Cada aviso lleva una clave que cambia si cambia la situacion, para que un
aviso leido vuelva a aparecer cuando hay algo nuevo que contar.
"""

from datetime import timedelta

from django.db.models import F, Max
from django.utils import timezone

from .models import MensajeContacto, NotificacionLeida, Oportunidad, Pedido, Pqrs, Producto, RequisitoNormativo
from .permisos import VER, puede, rol_de

DIAS_SIN_CONTACTO = 7
DIAS_PEDIDOS = 7


def _iso(fecha):
    return fecha.isoformat() if fecha else None


def _inventario():
    for p in Producto.objects.filter(stock__lte=F("stock_minimo")).order_by("stock"):
        yield {
            "clave": f"stock:{p.id}:{p.stock}",
            "tipo": "inventario",
            "titulo": "Stock mínimo",
            "texto": f"{p.nombre}: quedan {p.stock} (mínimo {p.stock_minimo}).",
            "fecha": None,
            "ruta": "/inventario",
            "prioridad": 2,
        }


def _normativa():
    hoy = timezone.localdate()
    pendientes = RequisitoNormativo.objects.exclude(estado="Cumplido").filter(
        fecha_vencimiento__isnull=False, fecha_vencimiento__lte=hoy + timedelta(days=30)
    )
    for r in pendientes:
        dias = (r.fecha_vencimiento - hoy).days
        vencido = dias < 0
        if vencido:
            texto = f"{r.nombre} ante {r.autoridad} venció hace {-dias} {'día' if dias == -1 else 'días'}."
        elif dias == 0:
            texto = f"{r.nombre} ante {r.autoridad} vence hoy."
        else:
            texto = f"{r.nombre} ante {r.autoridad} vence en {dias} {'día' if dias == 1 else 'días'}."
        yield {
            "clave": f"norma:{r.id}:{'vencido' if vencido else 'proximo'}:{r.fecha_vencimiento.isoformat()}",
            "tipo": "normativa",
            "titulo": "Requisito vencido" if vencido else "Vence pronto",
            "texto": texto,
            "fecha": None,
            "ruta": "/normativa",
            "prioridad": 0 if vencido else 1,
        }


def _tienda():
    desde = timezone.now() - timedelta(days=DIAS_PEDIDOS)
    for p in Pedido.objects.filter(estado="Pagado", pagado_en__gte=desde).select_related("cliente"):
        yield {
            "clave": f"pedido:{p.id}",
            "tipo": "tienda",
            "titulo": "Pedido pagado",
            "texto": f"Pedido #{p.id} de {p.cliente.nombre} por $ {p.total:,.0f}. Programe el despacho.".replace(",", "."),
            "fecha": _iso(p.pagado_en),
            "ruta": "/tienda",
            "prioridad": 1,
        }


def _crm(usuario):
    abiertas = Oportunidad.objects.exclude(etapa__in=["Ganada", "Perdida"]).select_related("cliente")
    # El comercial ve las suyas y las que no tienen responsable; gerencia, todas.
    if rol_de(usuario) == "Comercial":
        empleado = getattr(usuario, "empleado", None)
        abiertas = abiertas.filter(responsable__isnull=True) | abiertas.filter(responsable=empleado)
    abiertas = abiertas.annotate(ultimo=Max("interacciones__fecha"))
    ahora = timezone.now()
    for op in abiertas:
        ultimo = op.ultimo or op.creado
        dias = (ahora - ultimo).days
        if dias < DIAS_SIN_CONTACTO:
            continue
        yield {
            "clave": f"crm:{op.id}:{dias // DIAS_SIN_CONTACTO}",
            "tipo": "crm",
            "titulo": "Oportunidad sin contacto",
            "texto": f"Lleva {dias} días sin contacto con {op.cliente.nombre} ({op.titulo}).",
            "fecha": _iso(ultimo),
            "ruta": f"/clientes/{op.cliente_id}",
            "prioridad": 2,
        }


def _atencion():
    hoy = timezone.now()
    for q in Pqrs.objects.filter(estado__in=["Recibida", "EnTramite"]):
        dias = (hoy - q.creada).days
        yield {
            "clave": f"pqrs:{q.id}:{q.estado}",
            "tipo": "pqrs",
            "titulo": f"{q.get_tipo_display()} sin responder",
            "texto": f"{q.radicado} de {q.nombre}" + (f" · radicada hace {dias} {'día' if dias == 1 else 'días'}." if dias else " · radicada hoy."),
            "fecha": _iso(q.creada),
            "ruta": "/atencion",
            "prioridad": 1 if dias >= 5 else 2,
        }
    for m in MensajeContacto.objects.filter(atendido=False):
        yield {
            "clave": f"contacto:{m.id}",
            "tipo": "pqrs",
            "titulo": "Mensaje de contacto",
            "texto": f"{m.nombre} escribió desde el sitio web.",
            "fecha": _iso(m.creado),
            "ruta": "/atencion",
            "prioridad": 2,
        }


FUENTES = [("productos", lambda u: _inventario()), ("normativa", lambda u: _normativa()),
           ("pedidos", lambda u: _tienda()), ("crm", _crm), ("pqrs", lambda u: _atencion())]


def avisos_de(usuario):
    """Lista de avisos del usuario, los mas urgentes primero, con su marca de leido."""
    avisos = []
    for modulo, fuente in FUENTES:
        if puede(usuario, modulo, VER):
            avisos.extend(fuente(usuario))
    leidas = set(NotificacionLeida.objects.filter(
        usuario=usuario, clave__in=[a["clave"] for a in avisos]
    ).values_list("clave", flat=True))
    for aviso in avisos:
        aviso["leida"] = aviso["clave"] in leidas
    avisos.sort(key=lambda a: (a["leida"], a["prioridad"]))
    return avisos


def marcar_leidas(usuario, claves):
    existentes = set(NotificacionLeida.objects.filter(usuario=usuario, clave__in=claves).values_list("clave", flat=True))
    NotificacionLeida.objects.bulk_create(
        [NotificacionLeida(usuario=usuario, clave=c) for c in set(claves) - existentes]
    )
