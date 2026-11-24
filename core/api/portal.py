"""
API del portal de clientes (/api/v1/portal/...).

Un cliente entra con su NIT o documento y solo ve SUS datos: todo se filtra
por request.user.cliente, nunca por un id que llegue en la peticion. Asi un
cliente no puede consultar compras de otro cambiando un numero en la URL.

- GET  portal/resumen/              datos del cliente, compras y solicitudes
- GET  portal/catalogo/             productos con precio vigente
- POST portal/cotizaciones/         solicita una cotizacion -> oportunidad en el CRM
- GET  portal/compras/<id>/comprobante/  comprobante de venta en PDF
"""

from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_spectacular.utils import extend_schema
from rest_framework import serializers, status
from rest_framework.permissions import BasePermission
from rest_framework.response import Response
from rest_framework.views import APIView

from ..exportadores import Columna, exportar_pdf
from ..models import Interaccion, Oportunidad, Producto, Venta
from ..permisos import ROL_CLIENTE, rol_de

# Lo que ve el cliente de cada etapa del CRM: sin probabilidades ni notas internas.
ESTADO_PARA_EL_CLIENTE = {
    "Prospecto": "Recibida",
    "Contactado": "En revisión",
    "Cotizacion": "Cotización enviada",
    "Negociacion": "En negociación",
    "Ganada": "Aceptada",
    "Perdida": "Cerrada",
}


def numero_venta(venta):
    return f"V-{venta.id:04d}"


class EsCliente(BasePermission):
    message = "Esta seccion es solo para clientes con acceso al portal."

    def has_permission(self, request, view):
        usuario = request.user
        return bool(
            usuario and usuario.is_authenticated and rol_de(usuario) == ROL_CLIENTE
            and getattr(usuario, "cliente", None) is not None
        )


class BasePortal(APIView):
    permission_classes = [EsCliente]


@extend_schema(tags=["Portal de clientes"], summary="Resumen del cliente: datos, compras y solicitudes")
class ResumenPortalView(BasePortal):
    def get(self, request):
        cliente = request.user.cliente
        ventas = (
            Venta.objects.filter(cliente=cliente).exclude(estado="Anulada")
            .prefetch_related("detalles__producto").order_by("-fecha")
        )
        solicitudes = cliente.oportunidades.filter(origen="Portal").order_by("-creado")
        return Response({
            "cliente": {
                "nombre": cliente.nombre, "documento": cliente.documento,
                "empresa": cliente.empresa, "correo": cliente.correo,
            },
            "compras": [
                {
                    "id": v.id, "numero": numero_venta(v), "fecha": v.fecha.date().isoformat(),
                    "total": v.total, "estado": v.estado,
                    "productos": [f"{d.producto.nombre} × {d.cantidad}" for d in v.detalles.all()],
                }
                for v in ventas
            ],
            "solicitudes": [
                {
                    "id": o.id, "titulo": o.titulo, "fecha": o.creado.date().isoformat(),
                    "estado": ESTADO_PARA_EL_CLIENTE[o.etapa], "valor_estimado": o.valor_estimado,
                }
                for o in solicitudes
            ],
        })


@extend_schema(tags=["Portal de clientes"], summary="Catalogo con precios vigentes")
class CatalogoPortalView(BasePortal):
    def get(self, request):
        productos = Producto.objects.order_by("categoria", "nombre")
        return Response([
            {
                "id": p.id, "codigo": p.codigo, "nombre": p.nombre, "categoria": p.categoria,
                "precio": p.precio_venta, "disponible": p.stock > 0,
            }
            for p in productos
        ])


class ItemCotizacionSerializer(serializers.Serializer):
    producto = serializers.PrimaryKeyRelatedField(queryset=Producto.objects.all())
    cantidad = serializers.IntegerField(min_value=1, max_value=100000)


class CotizacionSerializer(serializers.Serializer):
    items = ItemCotizacionSerializer(many=True, allow_empty=False)
    fecha_entrega = serializers.DateField(required=False, allow_null=True)
    observaciones = serializers.CharField(required=False, allow_blank=True, max_length=500)

    def validate_fecha_entrega(self, valor):
        if valor and valor < timezone.localdate():
            raise serializers.ValidationError("La fecha de entrega no puede estar en el pasado.")
        return valor

    def validate_items(self, items):
        if len(items) > 20:
            raise serializers.ValidationError("Máximo 20 productos por solicitud.")
        return items


@extend_schema(
    tags=["Portal de clientes"],
    summary="Solicitar una cotizacion",
    description=(
        "Crea una oportunidad en la etapa Prospecto del CRM (origen Portal) con el "
        "valor estimado a precios vigentes, y registra la solicitud como "
        "interaccion del cliente. El equipo comercial la ve en el CRM."
    ),
    request=CotizacionSerializer,
)
class CotizacionPortalView(BasePortal):
    def post(self, request):
        datos = CotizacionSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        cliente = request.user.cliente
        items = datos.validated_data["items"]
        lineas = [f"{i['producto'].nombre} × {i['cantidad']}" for i in items]
        valor = sum((i["producto"].precio_venta * i["cantidad"] for i in items), Decimal("0"))
        entrega = datos.validated_data.get("fecha_entrega")
        observaciones = datos.validated_data.get("observaciones", "").strip()

        notas = "Solicitud desde el portal de clientes.\nProductos:\n- " + "\n- ".join(lineas)
        if entrega:
            notas += f"\nFecha de entrega deseada: {entrega:%d/%m/%Y}"
        if observaciones:
            notas += f"\nObservaciones del cliente: {observaciones}"

        titulo = "Cotización portal: " + ", ".join(i["producto"].nombre for i in items)
        with transaction.atomic():
            oportunidad = Oportunidad.objects.create(
                cliente=cliente, titulo=titulo[:150], etapa="Prospecto", origen="Portal",
                valor_estimado=valor, fecha_cierre_estimada=entrega, notas=notas,
            )
            Interaccion.objects.create(
                cliente=cliente, oportunidad=oportunidad, tipo="Portal",
                descripcion=("Solicitó cotización: " + "; ".join(lineas))[:500],
                proxima_accion="Enviar la cotización al cliente",
                registrado_por=request.user,
            )
        return Response(
            {"id": oportunidad.id, "estado": ESTADO_PARA_EL_CLIENTE["Prospecto"], "valor_estimado": valor},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Portal de clientes"], summary="Comprobante de una compra en PDF")
class ComprobantePortalView(BasePortal):
    def get(self, request, pk):
        venta = get_object_or_404(
            Venta.objects.prefetch_related("detalles__producto"), pk=pk, cliente=request.user.cliente,
        )
        columnas = [
            Columna("Producto", lambda d: d.producto.nombre, 260, izquierda=True),
            Columna("Cantidad", lambda d: d.cantidad, 70),
            Columna("Precio unitario", lambda d: f"$ {d.precio_unitario:,.0f}".replace(",", "."), 100),
            Columna("Subtotal", lambda d: f"$ {d.subtotal:,.0f}".replace(",", "."), 100),
        ]
        titulo = (
            f"Comprobante de venta {numero_venta(venta)} · {venta.cliente.nombre} · "
            f"{venta.fecha:%d/%m/%Y} · Total $ {venta.total:,.0f}".replace(",", ".")
            + " (no reemplaza la factura electrónica)"
        )
        return exportar_pdf(venta.detalles.all(), columnas, titulo, f"comprobante_{numero_venta(venta)}")
