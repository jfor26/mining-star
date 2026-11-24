"""Sitio publico: PQRS con radicado, consulta privada, contacto y gestion interna."""

from django.contrib.auth.models import Group, User
from django.core.cache import cache
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cliente, MensajeContacto, Pqrs

PQRS = {
    "tipo": "Peticion", "nombre": "Ana Ruiz", "documento": "900500001", "correo": "ana@x.co",
    "detalle": "Quisiera conocer los horarios de despacho.", "autoriza_datos": True,
}


class PruebasDelSitioPublico(APITestCase):
    def setUp(self):
        cache.clear()
        self.cliente = Cliente.objects.create(documento="900500001", nombre="Vías", correo="v@v.co",
                                              telefono="3000000000", empresa="Obra")

    def test_radicar_asigna_radicado_consecutivo_y_vincula_al_cliente(self):
        r1 = self.client.post(reverse("api-publico-pqrs"), PQRS, format="json")
        r2 = self.client.post(reverse("api-publico-pqrs"), {**PQRS, "documento": "123"}, format="json")
        self.assertEqual(r1.status_code, status.HTTP_201_CREATED, r1.data)
        self.assertRegex(r1.data["radicado"], r"^PQRS-\d{4}-0001$")
        self.assertTrue(r2.data["radicado"].endswith("-0002"))
        self.assertEqual(Pqrs.objects.get(radicado=r1.data["radicado"]).cliente, self.cliente)

    def test_sin_autorizacion_de_datos_no_se_radica(self):
        r = self.client.post(reverse("api-publico-pqrs"), {**PQRS, "autoriza_datos": False}, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("autoriza_datos", r.data)

    def test_la_consulta_exige_el_documento_correcto(self):
        radicado = self.client.post(reverse("api-publico-pqrs"), PQRS, format="json").data["radicado"]
        url = reverse("api-publico-pqrs-consulta", args=[radicado])
        self.assertEqual(self.client.get(url, {"documento": "999"}).status_code, status.HTTP_404_NOT_FOUND)
        r = self.client.get(url, {"documento": "900500001"})
        self.assertEqual((r.status_code, r.data["estado"], r.data["respuesta"]), (200, "Recibida", ""))

    def test_contacto(self):
        r = self.client.post(reverse("api-publico-contacto"),
                             {"nombre": "Luis", "correo": "l@x.co", "mensaje": "Necesito una cotización."}, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED)
        self.assertEqual(MensajeContacto.objects.count(), 1)

    def test_limite_de_envios_por_ip(self):
        from django.test import override_settings
        from rest_framework.settings import api_settings
        tasas = {**api_settings.DEFAULT_THROTTLE_RATES, "publico": "2/hour"}
        with override_settings(REST_FRAMEWORK={**self._ajustes(), "DEFAULT_THROTTLE_RATES": tasas}):
            from rest_framework.throttling import ScopedRateThrottle
            ScopedRateThrottle.THROTTLE_RATES = tasas
            try:
                codigos = [self.client.post(reverse("api-publico-contacto"),
                                            {"nombre": "L", "correo": "l@x.co", "mensaje": "Mensaje de prueba"},
                                            format="json").status_code for _ in range(3)]
            finally:
                ScopedRateThrottle.THROTTLE_RATES = api_settings.DEFAULT_THROTTLE_RATES
        self.assertEqual(codigos, [201, 201, 429])

    def _ajustes(self):
        from django.conf import settings
        return settings.REST_FRAMEWORK

    def test_responder_y_luego_el_ciudadano_ve_la_respuesta(self):
        radicado = self.client.post(reverse("api-publico-pqrs"), PQRS, format="json").data["radicado"]
        comercial = User.objects.create_user(username="com", password="Comer*Mina2026")
        comercial.groups.add(Group.objects.get(name="Comercial"))
        self.client.force_authenticate(comercial)
        pqrs = Pqrs.objects.get(radicado=radicado)
        url = reverse("api-pqrs-detail", args=[pqrs.id])
        sin_texto = self.client.patch(url, {"estado": "Respondida"}, format="json")
        self.assertEqual(sin_texto.status_code, status.HTTP_400_BAD_REQUEST)
        ok = self.client.patch(url, {"estado": "Respondida", "respuesta": "Despachamos de lunes a sábado."}, format="json")
        self.assertEqual(ok.status_code, 200, ok.data)
        self.client.force_authenticate(None)
        r = self.client.get(reverse("api-publico-pqrs-consulta", args=[radicado]), {"documento": "900500001"})
        self.assertEqual(r.data["respuesta"], "Despachamos de lunes a sábado.")

    def test_operario_no_ve_las_pqrs(self):
        operario = User.objects.create_user(username="op", password="Opera*Mina2026")
        operario.groups.add(Group.objects.get(name="Operario"))
        self.client.force_authenticate(operario)
        self.assertEqual(self.client.get(reverse("api-pqrs-list")).status_code, status.HTTP_403_FORBIDDEN)
