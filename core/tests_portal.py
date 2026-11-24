"""Portal de clientes: acceso, aislamiento entre clientes y cotizaciones al CRM."""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cliente, DetalleVenta, Empleado, Interaccion, Oportunidad, Producto, Proveedor, Venta

CLAVE = "Portal*Mina2026"


class BasePortal(APITestCase):
    def setUp(self):
        proveedor = Proveedor.objects.create(nit="1", empresa="P", contacto="C", correo="p@p.co",
                                             telefono="3000000000", ciudad="Ibagué", direccion="x")
        self.producto = Producto.objects.create(
            proveedor=proveedor, codigo="REC-001", nombre="Recebo para vías", categoria="Agregados",
            precio_compra=Decimal("10000"), precio_venta=Decimal("30000"), stock=50, stock_minimo=5,
        )
        self.cliente = Cliente.objects.create(documento="900500001", nombre="Vías del Centro",
                                              correo="c@v.co", telefono="3000000000", empresa="Obra civil")
        self.otro = Cliente.objects.create(documento="900500002", nombre="Otro Cliente",
                                           correo="o@o.co", telefono="3000000001", empresa="X")
        vendedor = Empleado.objects.create(documento="1", nombres="Ana", apellidos="Paz", correo="a@ms.co",
                                           telefono="3000000002", cargo="Comercial", area="Comercial")
        self.venta_propia = self.vender(self.cliente, vendedor)
        self.venta_ajena = self.vender(self.otro, vendedor)

        admin = User.objects.create_user(username="admin.p", password="Admin*Mina2026")
        admin.groups.add(Group.objects.get(name="Administrador"))
        self.client.force_authenticate(admin)
        r = self.client.post(reverse("api-clientes-acceso-portal", args=[self.cliente.id]), {"clave": CLAVE}, format="json")
        self.assertEqual(r.status_code, 200, r.data)
        self.client.force_authenticate(None)

    def vender(self, cliente, vendedor):
        venta = Venta.objects.create(cliente=cliente, empleado=vendedor, total=Decimal("60000"))
        DetalleVenta.objects.create(venta=venta, producto=self.producto, cantidad=2,
                                    precio_unitario=Decimal("30000"), subtotal=Decimal("60000"))
        return venta

    def entrar_como_cliente(self):
        r = self.client.post(reverse("api-login"), {"username": "900500001", "password": CLAVE}, format="json")
        self.assertEqual(r.status_code, 200, r.data)
        self.assertEqual(r.data["usuario"]["rol"], "Cliente")
        self.assertEqual(r.data["usuario"]["permisos"], {})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {r.data['access']}")


class PruebasDelPortal(BasePortal):
    def test_el_cliente_ve_solo_sus_compras(self):
        self.entrar_como_cliente()
        datos = self.client.get(reverse("api-portal-resumen")).data
        self.assertEqual(datos["cliente"]["documento"], "900500001")
        self.assertEqual([c["id"] for c in datos["compras"]], [self.venta_propia.id])

    def test_no_puede_descargar_el_comprobante_de_otro_cliente(self):
        self.entrar_como_cliente()
        propio = self.client.get(reverse("api-portal-comprobante", args=[self.venta_propia.id]))
        self.assertEqual(propio.status_code, 200)
        self.assertEqual(propio["Content-Type"], "application/pdf")
        ajeno = self.client.get(reverse("api-portal-comprobante", args=[self.venta_ajena.id]))
        self.assertEqual(ajeno.status_code, 404)

    def test_el_cliente_no_entra_a_los_modulos_internos(self):
        self.entrar_como_cliente()
        for nombre in ["api-clientes-list", "api-ventas-list", "api-notificaciones"]:
            r = self.client.get(reverse(nombre))
            if nombre == "api-notificaciones":
                self.assertEqual(r.data["resultados"], [])
            else:
                self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN, nombre)

    def test_un_empleado_no_usa_el_portal(self):
        gerente = User.objects.create_user(username="g", password="Gerente*Mina2026")
        gerente.groups.add(Group.objects.get(name="Gerente"))
        self.client.force_authenticate(gerente)
        self.assertEqual(self.client.get(reverse("api-portal-resumen")).status_code, status.HTTP_403_FORBIDDEN)

    def test_cotizacion_crea_oportunidad_e_interaccion_en_el_crm(self):
        self.entrar_como_cliente()
        entrega = (timezone.localdate() + timedelta(days=5)).isoformat()
        r = self.client.post(reverse("api-portal-cotizaciones"), {
            "items": [{"producto": self.producto.id, "cantidad": 10}],
            "fecha_entrega": entrega, "observaciones": "Obra en Espinal",
        }, format="json")
        self.assertEqual(r.status_code, status.HTTP_201_CREATED, r.data)
        op = Oportunidad.objects.get(id=r.data["id"])
        self.assertEqual((op.cliente, op.etapa, op.origen, op.valor_estimado),
                         (self.cliente, "Prospecto", "Portal", Decimal("300000")))
        self.assertIn("Obra en Espinal", op.notas)
        self.assertTrue(Interaccion.objects.filter(oportunidad=op, tipo="Portal").exists())
        solicitudes = self.client.get(reverse("api-portal-resumen")).data["solicitudes"]
        self.assertEqual(solicitudes[0]["estado"], "Recibida")

    def test_cotizacion_invalida(self):
        self.entrar_como_cliente()
        ayer = (timezone.localdate() - timedelta(days=1)).isoformat()
        r = self.client.post(reverse("api-portal-cotizaciones"), {
            "items": [{"producto": self.producto.id, "cantidad": 0}], "fecha_entrega": ayer,
        }, format="json")
        self.assertEqual(r.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("fecha_entrega", r.data)
        self.assertEqual(Oportunidad.objects.count(), 0)

    def test_clave_debil_y_quitar_acceso(self):
        admin = User.objects.get(username="admin.p")
        self.client.force_authenticate(admin)
        url = reverse("api-clientes-acceso-portal", args=[self.otro.id])
        self.assertEqual(self.client.post(url, {"clave": "123"}, format="json").status_code, 400)
        self.client.delete(reverse("api-clientes-acceso-portal", args=[self.cliente.id]))
        self.client.force_authenticate(None)
        r = self.client.post(reverse("api-login"), {"username": "900500001", "password": CLAVE}, format="json")
        self.assertNotEqual(r.status_code, 200)

    def test_comercial_sin_permiso_de_editar_no_da_accesos(self):
        contador = User.objects.create_user(username="c", password="Conta*Mina2026")
        contador.groups.add(Group.objects.get(name="Contador"))
        self.client.force_authenticate(contador)
        r = self.client.post(reverse("api-clientes-acceso-portal", args=[self.otro.id]), {"clave": CLAVE}, format="json")
        self.assertEqual(r.status_code, status.HTTP_403_FORBIDDEN)


class PruebasDeFichaDelCliente(BasePortal):
    def test_ficha_completa_para_gerente(self):
        gerente = User.objects.create_user(username="g2", password="Gerente*Mina2026")
        gerente.groups.add(Group.objects.get(name="Gerente"))
        self.client.force_authenticate(gerente)
        Oportunidad.objects.create(cliente=self.cliente, titulo="Recebo", valor_estimado=Decimal("500"))
        Interaccion.objects.create(cliente=self.cliente, tipo="Llamada", descripcion="Seguimiento")
        datos = self.client.get(reverse("api-clientes-ficha", args=[self.cliente.id])).data
        self.assertEqual(datos["compras"]["total"], Decimal("60000"))
        self.assertEqual(datos["abiertas_valor"], Decimal("500"))
        self.assertEqual(datos["ultimo_contacto_dias"], 0)
        self.assertEqual(datos["interacciones"][0]["descripcion"], "Seguimiento")
        self.assertTrue(datos["cliente"]["acceso_portal"])

    def test_ficha_sin_crm_ni_ventas_para_auxiliar(self):
        auxiliar = User.objects.create_user(username="a2", password="Auxi*Mina2026")
        auxiliar.groups.add(Group.objects.get(name="Auxiliar"))
        self.client.force_authenticate(auxiliar)
        datos = self.client.get(reverse("api-clientes-ficha", args=[self.cliente.id])).data
        self.assertNotIn("compras", datos)
        self.assertNotIn("oportunidades", datos)
