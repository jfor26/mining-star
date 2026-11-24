"""Campana de notificaciones: avisos por cargo y marca de leido."""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cliente, Interaccion, Oportunidad, Producto, Proveedor, RequisitoNormativo


class PruebasDeNotificaciones(APITestCase):
    def setUp(self):
        self.url = reverse("api-notificaciones")
        proveedor = Proveedor.objects.create(nit="1", empresa="P", contacto="C", correo="p@p.co",
                                             telefono="3000000000", ciudad="Ibagué", direccion="x")
        Producto.objects.create(proveedor=proveedor, codigo="P-1", nombre="Recebo", categoria="Agregados",
                                precio_compra=Decimal("1"), precio_venta=Decimal("2"), stock=2, stock_minimo=5)
        RequisitoNormativo.objects.create(
            autoridad="ANM", categoria="Minero", nombre="Regalías", norma="Ley 685", descripcion="x",
            fecha_vencimiento=timezone.localdate() - timedelta(days=3),
        )
        cliente = Cliente.objects.create(documento="900", nombre="Ferretería X", correo="f@x.co",
                                         telefono="3000000000", empresa="X")
        self.op = Oportunidad.objects.create(cliente=cliente, titulo="Recebo vía", valor_estimado=Decimal("1000"))
        Oportunidad.objects.filter(pk=self.op.pk).update(creado=timezone.now() - timedelta(days=10))

    def entrar(self, cargo):
        usuario = User.objects.create_user(username=f"u_{cargo}", password="Prueba2026*x")
        usuario.groups.add(Group.objects.get(name=cargo))
        self.client.force_authenticate(usuario)
        return usuario

    def tipos(self):
        return {a["tipo"] for a in self.client.get(self.url).data["resultados"]}

    def test_cada_cargo_ve_solo_sus_modulos(self):
        self.entrar("Supervisor")
        self.assertEqual(self.tipos(), {"inventario", "normativa"})
        self.entrar("Comercial")
        self.assertEqual(self.tipos(), {"inventario", "crm"})
        self.entrar("Operario")
        self.assertEqual(self.tipos(), set())

    def test_textos_de_los_avisos(self):
        self.entrar("Gerente")
        textos = " ".join(a["texto"] for a in self.client.get(self.url).data["resultados"])
        self.assertIn("Recebo: quedan 2 (mínimo 5)", textos)
        self.assertIn("venció hace 3 días", textos)
        self.assertIn("Lleva 10 días sin contacto con Ferretería X", textos)

    def test_un_contacto_reciente_quita_el_aviso_de_crm(self):
        self.entrar("Gerente")
        Interaccion.objects.create(cliente=self.op.cliente, oportunidad=self.op, tipo="Llamada", descripcion="ok")
        self.assertNotIn("crm", self.tipos())

    def test_marcar_todo_como_leido(self):
        self.entrar("Gerente")
        self.assertEqual(self.client.get(self.url).data["sin_leer"], 3)
        respuesta = self.client.post(self.url, {"todas": True}, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(self.client.get(self.url).data["sin_leer"], 0)

    def test_si_baja_mas_el_stock_el_aviso_vuelve(self):
        self.entrar("Gerente")
        self.client.post(self.url, {"todas": True}, format="json")
        Producto.objects.filter(codigo="P-1").update(stock=1)
        self.assertEqual(self.client.get(self.url).data["sin_leer"], 1)

    def test_claves_invalidas(self):
        self.entrar("Gerente")
        respuesta = self.client.post(self.url, {"claves": "no-es-lista"}, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_sin_sesion_responde_401(self):
        self.assertEqual(self.client.get(self.url).status_code, status.HTTP_401_UNAUTHORIZED)
