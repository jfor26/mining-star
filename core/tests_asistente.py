"""Asistente por reglas: respuestas con datos reales y respeto de permisos."""

from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.urls import reverse
from rest_framework.test import APITestCase

from .asistente import normalizar, responder
from .models import Producto, Proveedor


class PruebasDelAsistente(APITestCase):
    def setUp(self):
        proveedor = Proveedor.objects.create(nit="1", empresa="P", contacto="C", correo="p@p.co",
                                             telefono="3000000000", ciudad="Ibagué", direccion="x")
        Producto.objects.create(proveedor=proveedor, codigo="REC-001", nombre="Recebo para vías", categoria="Agregados",
                                precio_compra=Decimal("1"), precio_venta=Decimal("2"), stock=3, stock_minimo=10)

    def usuario(self, cargo):
        u = User.objects.create_user(username=f"a_{cargo}", password="Prueba*2026x", first_name="Ana")
        u.groups.add(Group.objects.get(name=cargo))
        return u

    def test_normalizar_quita_tildes_y_signos(self):
        self.assertEqual(normalizar("¿Cuánto STOCK hay?").strip(), "cuanto stock hay")

    def test_stock_minimo_con_datos_reales(self):
        r = responder(self.usuario("Gerente"), "¿Qué productos están en stock mínimo?")
        self.assertIn("Recebo para vías (3)", r["respuesta"])
        self.assertEqual(r["fuente"], "Inventario")

    def test_respeta_los_permisos_del_cargo(self):
        r = responder(self.usuario("Operario"), "¿Cuál fue la última venta?")
        self.assertEqual(r["respuesta"], "Su cargo no tiene acceso a esa información.")

    def test_pregunta_desconocida(self):
        self.assertIn("No entendí", responder(self.usuario("Gerente"), "qué tal el clima")["respuesta"])

    def test_api_y_clientes_del_portal_no_lo_usan(self):
        self.client.force_authenticate(self.usuario("Gerente"))
        r = self.client.post(reverse("api-asistente"), {"pregunta": "hola"}, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertIn("Hola, Ana", r.data["respuesta"])
        self.client.force_authenticate(self.usuario("Cliente"))
        self.assertEqual(self.client.post(reverse("api-asistente"), {"pregunta": "hola"}, format="json").status_code, 403)
