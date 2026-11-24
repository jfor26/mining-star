"""
API publica del sitio de la empresa (sin iniciar sesion) y gestion interna
de PQRS y mensajes de contacto.

Publico (limitado por IP con el throttle "publico"):
- POST publico/pqrs/                       radica una PQRS y devuelve el radicado
- GET  publico/pqrs/<radicado>/?documento= consulta el estado (pide el documento
                                           con que se radico, para que nadie mas
                                           pueda leer la respuesta)
- POST publico/contacto/                   mensaje del formulario de contacto

Interno (modulo "pqrs" de la matriz de acceso):
- /pqrs/        listar, ver y responder (PATCH estado y respuesta)
- /contactos/   listar y marcar como atendido
"""

from django.db import IntegrityError, transaction
from django.shortcuts import get_object_or_404
from drf_spectacular.utils import extend_schema
from rest_framework import mixins, serializers, status, viewsets
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView

from ..models import Cliente, MensajeContacto, Pqrs
from ..permisos import PermisoPorModulo


class BasePublica(APIView):
    permission_classes = [AllowAny]
    authentication_classes = []
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "publico"


class PqrsPublicaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pqrs
        fields = ["tipo", "nombre", "documento", "correo", "telefono", "detalle", "autoriza_datos"]

    def validate_documento(self, valor):
        valor = valor.strip()
        if not valor.isdigit():
            raise serializers.ValidationError("El documento o NIT solo admite dígitos.")
        return valor

    def validate_autoriza_datos(self, valor):
        if not valor:
            raise serializers.ValidationError("Debe autorizar el tratamiento de sus datos para radicar la solicitud.")
        return valor

    def validate_detalle(self, valor):
        if len(valor.strip()) < 10:
            raise serializers.ValidationError("Describa su solicitud con al menos 10 caracteres.")
        return valor.strip()


@extend_schema(tags=["Sitio publico"], summary="Radicar una PQRS", request=PqrsPublicaSerializer)
class RadicarPqrsView(BasePublica):
    def post(self, request):
        datos = PqrsPublicaSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        cliente = Cliente.objects.filter(documento=datos.validated_data["documento"]).first()
        # Dos radicaciones simultaneas podrian calcular el mismo consecutivo:
        # el radicado es unico, asi que se reintenta.
        for _ in range(3):
            try:
                with transaction.atomic():
                    pqrs = datos.save(cliente=cliente)
                break
            except IntegrityError:
                datos.instance = None
        else:
            return Response({"mensaje": "Intente de nuevo en un momento."}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response(
            {"radicado": pqrs.radicado, "estado": pqrs.get_estado_display(), "creada": pqrs.creada},
            status=status.HTTP_201_CREATED,
        )


@extend_schema(tags=["Sitio publico"], summary="Consultar el estado de una PQRS")
class ConsultarPqrsView(BasePublica):
    def get(self, request, radicado):
        documento = (request.query_params.get("documento") or "").strip()
        pqrs = get_object_or_404(Pqrs, radicado=radicado.strip().upper(), documento=documento)
        return Response({
            "radicado": pqrs.radicado, "tipo": pqrs.get_tipo_display(), "estado": pqrs.get_estado_display(),
            "creada": pqrs.creada, "actualizada": pqrs.actualizada,
            "respuesta": pqrs.respuesta if pqrs.estado in ("Respondida", "Cerrada") else "",
        })


class ContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MensajeContacto
        fields = ["nombre", "correo", "telefono", "mensaje"]

    def validate_mensaje(self, valor):
        if len(valor.strip()) < 10:
            raise serializers.ValidationError("Escriba un mensaje de al menos 10 caracteres.")
        return valor.strip()


@extend_schema(tags=["Sitio publico"], summary="Enviar un mensaje de contacto", request=ContactoSerializer)
class ContactoView(BasePublica):
    def post(self, request):
        datos = ContactoSerializer(data=request.data)
        datos.is_valid(raise_exception=True)
        datos.save()
        return Response({"mensaje": "Recibimos su mensaje. Le responderemos pronto."}, status=status.HTTP_201_CREATED)


# ---------- Gestion interna ----------

class PqrsSerializer(serializers.ModelSerializer):
    tipo_texto = serializers.CharField(source="get_tipo_display", read_only=True)
    estado_texto = serializers.CharField(source="get_estado_display", read_only=True)
    cliente_nombre = serializers.CharField(source="cliente.nombre", read_only=True, default=None)
    respondida_por_nombre = serializers.SerializerMethodField()

    class Meta:
        model = Pqrs
        fields = [
            "id", "radicado", "tipo", "tipo_texto", "nombre", "documento", "correo", "telefono", "detalle",
            "cliente", "cliente_nombre", "estado", "estado_texto", "respuesta", "respondida_por_nombre",
            "creada", "actualizada",
        ]
        read_only_fields = [f for f in fields if f not in ("estado", "respuesta")]

    def get_respondida_por_nombre(self, pqrs):
        u = pqrs.respondida_por
        return (u.get_full_name() or u.username) if u else None

    def validate(self, datos):
        estado = datos.get("estado", getattr(self.instance, "estado", None))
        respuesta = datos.get("respuesta", getattr(self.instance, "respuesta", ""))
        if estado in ("Respondida", "Cerrada") and not (respuesta or "").strip():
            raise serializers.ValidationError({"respuesta": "Escriba la respuesta antes de marcarla como respondida."})
        return datos


@extend_schema(tags=["Atencion al cliente"])
class PqrsViewSet(mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [PermisoPorModulo]
    modulo = "pqrs"
    serializer_class = PqrsSerializer
    queryset = Pqrs.objects.select_related("cliente", "respondida_por")
    filterset_fields = ["estado", "tipo"]

    def perform_update(self, serializer):
        cambios = {}
        if serializer.validated_data.get("respuesta"):
            cambios["respondida_por"] = self.request.user
        serializer.save(**cambios)


class MensajeContactoSerializer(serializers.ModelSerializer):
    class Meta:
        model = MensajeContacto
        fields = ["id", "nombre", "correo", "telefono", "mensaje", "atendido", "creado"]
        read_only_fields = ["id", "nombre", "correo", "telefono", "mensaje", "creado"]


@extend_schema(tags=["Atencion al cliente"])
class MensajeContactoViewSet(mixins.ListModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet):
    permission_classes = [PermisoPorModulo]
    modulo = "pqrs"
    serializer_class = MensajeContactoSerializer
    queryset = MensajeContacto.objects.all()
    filterset_fields = ["atendido"]
