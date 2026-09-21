"""
Pruebas automatizadas de Mining Star.

Cubren lo que mas duele si se rompe: que nadie entre sin iniciar sesion,
que no se pueda borrar con un GET, y que el inventario nunca quede en
negativo ni descuadrado.

Ejecutar con:  python manage.py test
"""

from datetime import timedelta
from decimal import Decimal

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import (
    Cliente,
    DetalleVenta,
    Empleado,
    Producto,
    Proveedor,
    RegistroProduccion,
    Venta,
)


class BaseConSesion(TestCase):
    """Crea un usuario y dos registros de apoyo para las demas pruebas."""

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="operario", password="clave-de-prueba-123"
        )
        self.cliente = Cliente.objects.create(
            documento="1085123456",
            nombre="Constructora Nariño",
            correo="contacto@constructora.co",
            telefono="3001234567",
            empresa="Constructora Nariño S.A.S.",
        )
        self.proveedor = Proveedor.objects.create(
            nit="900123456-1",
            empresa="Insumos Andinos",
            contacto="Ana Ruiz",
            correo="ventas@insumos.co",
            telefono="3009876543",
            ciudad="Pasto",
            direccion="Calle 18 #25-40",
        )
        self.producto = Producto.objects.create(
            codigo="EXP-001",
            nombre="Explosivo industrial",
            categoria="Insumos",
            proveedor=self.proveedor,
            precio_compra=Decimal("100000.00"),
            precio_venta=Decimal("150000.00"),
            stock=10,
            stock_minimo=2,
        )

    def iniciar_sesion(self):
        self.client.login(username="operario", password="clave-de-prueba-123")


# =========================================================
# AUTENTICACION
# =========================================================

class PruebasDeAcceso(BaseConSesion):

    def test_el_dashboard_exige_sesion(self):
        """Sin iniciar sesion, /dashboard/ debe redirigir al login."""
        respuesta = self.client.get(reverse("dashboard"))
        self.assertEqual(respuesta.status_code, 302)
        self.assertIn(reverse("login"), respuesta.url)

    def test_las_exportaciones_exigen_sesion(self):
        """Los reportes traen datos personales: no pueden ser publicos."""
        for ruta in [
            "exportar_clientes_excel",
            "exportar_clientes_pdf",
            "exportar_empleados_excel",
            "exportar_empleados_pdf",
        ]:
            with self.subTest(ruta=ruta):
                respuesta = self.client.get(reverse(ruta))
                self.assertEqual(respuesta.status_code, 302)

    def test_login_con_credenciales_correctas(self):
        respuesta = self.client.post(
            reverse("login"),
            {"usuario": "operario", "contrasena": "clave-de-prueba-123"},
        )
        self.assertEqual(respuesta.status_code, 302)
        self.assertEqual(respuesta.url, reverse("dashboard"))

    def test_login_con_credenciales_incorrectas(self):
        respuesta = self.client.post(
            reverse("login"),
            {"usuario": "operario", "contrasena": "equivocada"},
        )
        # Se queda en la pagina y no crea sesion.
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_admin_1234_ya_no_sirve(self):
        """Las credenciales que estaban escritas en el JavaScript."""
        respuesta = self.client.post(
            reverse("login"), {"usuario": "admin", "contrasena": "1234"}
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertNotIn("_auth_user_id", self.client.session)


# =========================================================
# BORRADO
# =========================================================

class PruebasDeBorrado(BaseConSesion):

    def test_no_se_puede_borrar_con_get(self):
        """Un GET a la URL de borrado debe ser rechazado con 405."""
        self.iniciar_sesion()
        respuesta = self.client.get(
            reverse("eliminar_cliente", args=[self.cliente.id])
        )
        self.assertEqual(respuesta.status_code, 405)
        self.assertTrue(Cliente.objects.filter(pk=self.cliente.pk).exists())

    def test_se_puede_borrar_con_post(self):
        self.iniciar_sesion()
        respuesta = self.client.post(
            reverse("eliminar_cliente", args=[self.cliente.id])
        )
        self.assertEqual(respuesta.status_code, 302)
        self.assertFalse(Cliente.objects.filter(pk=self.cliente.pk).exists())

    def test_no_se_borra_un_cliente_con_ventas(self):
        """on_delete=PROTECT debe impedirlo, sin reventar con error 500."""
        self.iniciar_sesion()
        Venta.objects.create(cliente=self.cliente, total=Decimal("1000"))

        respuesta = self.client.post(
            reverse("eliminar_cliente", args=[self.cliente.id])
        )
        self.assertEqual(respuesta.status_code, 302)
        self.assertTrue(Cliente.objects.filter(pk=self.cliente.pk).exists())


# =========================================================
# VENTAS
# =========================================================

class PruebasDeVentas(BaseConSesion):

    def registrar(self, cantidad):
        return self.client.post(reverse("ventas"), {
            "cliente": self.cliente.id,
            "producto": self.producto.id,
            "cantidad": cantidad,
        })

    def test_venta_valida_descuenta_stock(self):
        self.iniciar_sesion()
        self.registrar(3)

        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 7)
        self.assertEqual(Venta.objects.count(), 1)
        self.assertEqual(
            Venta.objects.first().total, Decimal("450000.00")
        )

    def test_no_se_puede_vender_mas_de_lo_que_hay(self):
        """El bug original vendia igual y dejaba el stock en 0."""
        self.iniciar_sesion()
        self.registrar(50)

        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)      # intacto
        self.assertEqual(Venta.objects.count(), 0)     # no se registro nada
        self.assertEqual(DetalleVenta.objects.count(), 0)

    def test_no_se_puede_vender_cantidad_cero(self):
        self.iniciar_sesion()
        self.registrar(0)
        self.assertEqual(Venta.objects.count(), 0)

    def test_eliminar_venta_devuelve_el_stock_y_responde(self):
        """El bug original: la vista no tenia return y daba error 500."""
        self.iniciar_sesion()
        self.registrar(4)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 6)

        venta = Venta.objects.first()
        respuesta = self.client.post(
            reverse("eliminar_venta", args=[venta.id])
        )

        self.assertEqual(respuesta.status_code, 302)   # antes: 500
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)
        self.assertEqual(Venta.objects.count(), 0)


# =========================================================
# VALIDACION DE DATOS
# =========================================================

class PruebasDeValidacion(BaseConSesion):

    def test_documento_repetido_no_rompe_la_aplicacion(self):
        """Antes lanzaba IntegrityError (error 500). Ahora es un aviso."""
        self.iniciar_sesion()
        respuesta = self.client.post(reverse("clientes"), {
            "documento": self.cliente.documento,   # repetido
            "nombre": "Otro nombre",
            "correo": "otro@correo.co",
            "telefono": "3000000000",
            "empresa": "Otra empresa",
        })
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(Cliente.objects.count(), 1)

    def test_correo_invalido_se_rechaza(self):
        self.iniciar_sesion()
        self.client.post(reverse("clientes"), {
            "documento": "999999",
            "nombre": "Prueba",
            "correo": "esto-no-es-un-correo",
            "telefono": "3000000000",
            "empresa": "Prueba S.A.",
        })
        self.assertEqual(Cliente.objects.count(), 1)   # no se creo el segundo

    def test_precio_de_venta_menor_al_de_compra_se_rechaza(self):
        self.iniciar_sesion()
        self.client.post(reverse("nuevo_producto"), {
            "codigo": "X-1",
            "nombre": "Producto con perdida",
            "categoria": "Insumos",
            "proveedor": self.proveedor.id,
            "precio_compra": "100000",
            "precio_venta": "50000",
            "stock": "5",
            "stock_minimo": "1",
        })
        self.assertEqual(Producto.objects.count(), 1)  # solo el del setUp


# =========================================================
# RENDERIZADO DE PLANTILLAS
# =========================================================

class PruebasDeRenderizado(BaseConSesion):
    """Abre todas las pantallas y comprueba que no revientan.

    Es la red de seguridad de la reestructuracion de plantillas: si una
    herencia de base.html o una etiqueta {% url %} queda mal escrita,
    esta prueba lo detecta antes que el usuario.
    """

    PANTALLAS = [
        ("dashboard", None),
        ("clientes", None),
        ("editar_cliente", "cliente"),
        ("empleados", None),
        ("productos", None),
        ("nuevo_producto", None),
        ("editar_producto", "producto"),
        ("proveedores", None),
        ("editar_proveedor", "proveedor"),
        ("ventas", None),
        ("produccion", None),
        ("reportes", None),
    ]

    def test_todas_las_pantallas_responden_200(self):
        self.iniciar_sesion()

        for nombre, atributo in self.PANTALLAS:
            with self.subTest(pantalla=nombre):
                if atributo:
                    objeto = getattr(self, atributo)
                    url = reverse(nombre, args=[objeto.id])
                else:
                    url = reverse(nombre)

                respuesta = self.client.get(url)
                self.assertEqual(
                    respuesta.status_code, 200,
                    f"La pantalla '{nombre}' devolvio {respuesta.status_code}",
                )

    def test_la_pantalla_de_login_responde(self):
        respuesta = self.client.get(reverse("login"))
        self.assertEqual(respuesta.status_code, 200)

    def test_los_reportes_se_generan(self):
        """Excel y PDF deben construirse sin excepciones."""
        self.iniciar_sesion()

        for nombre, tipo in [
            ("exportar_clientes_excel", "spreadsheetml"),
            ("exportar_clientes_pdf", "pdf"),
            ("exportar_productos_excel", "spreadsheetml"),
            ("exportar_productos_pdf", "pdf"),
            ("exportar_proveedores_excel", "spreadsheetml"),
            ("exportar_proveedores_pdf", "pdf"),
            ("exportar_empleados_excel", "spreadsheetml"),
            ("exportar_empleados_pdf", "pdf"),
        ]:
            with self.subTest(reporte=nombre):
                respuesta = self.client.get(reverse(nombre))
                self.assertEqual(respuesta.status_code, 200)
                self.assertIn(tipo, respuesta["Content-Type"])
                self.assertGreater(len(respuesta.content), 500)


# =========================================================
# PRODUCCION DIARIA (HU-001)
# =========================================================

class PruebasDeProduccion(BaseConSesion):
    """Criterios de aceptacion de la HU-001 y validaciones del formulario."""

    def setUp(self):
        super().setUp()
        self.iniciar_sesion()
        self.supervisor = Empleado.objects.create(
            documento="1085777666", nombres="Carlos", apellidos="Munoz",
            correo="carlos@miningstar.co", telefono="3104445566",
            cargo="Supervisor", area="Operaciones",
        )
        self.hoy = timezone.localdate()

    def registrar(self, **cambios):
        datos = {"fecha": self.hoy.isoformat(), "turno": "Manana", "material": "Marmol",
                 "unidad": "t", "cantidad": "35.50", "supervisor": self.supervisor.id,
                 "observaciones": "Frente norte"}
        datos.update(cambios)
        return self.client.post(reverse("produccion"), datos)

    def test_registro_valido_se_guarda_con_el_usuario(self):
        respuesta = self.registrar()
        self.assertEqual(respuesta.status_code, 302)
        registro = RegistroProduccion.objects.get()
        self.assertEqual(registro.cantidad, Decimal("35.50"))
        self.assertEqual(registro.registrado_por, self.usuario)

    def test_el_registro_aparece_en_el_reporte_diario(self):
        self.registrar()
        respuesta = self.client.get(reverse("produccion"), {"fecha": self.hoy.isoformat()})
        self.assertContains(respuesta, "Frente norte")
        self.assertContains(respuesta, "Total del día")

    def test_el_stock_de_materia_prima_suma_los_turnos(self):
        self.registrar(turno="Manana", cantidad="30")
        self.registrar(turno="Tarde", cantidad="12.5")
        self.registrar(turno="Tarde", material="Caliza", cantidad="8")
        from .servicios import stock_materia_prima
        stock = {(f["material"], f["unidad"]): f["total"] for f in stock_materia_prima()}
        self.assertEqual(stock[("Marmol", "t")], Decimal("42.50"))
        self.assertEqual(stock[("Caliza", "t")], Decimal("8.00"))

    def test_cantidad_cero_o_negativa_se_rechaza(self):
        for valor in ["0", "-3"]:
            with self.subTest(cantidad=valor):
                self.assertEqual(self.registrar(cantidad=valor).status_code, 200)
        self.assertEqual(RegistroProduccion.objects.count(), 0)

    def test_cantidad_excesiva_se_rechaza(self):
        self.assertEqual(self.registrar(cantidad="5000.01").status_code, 200)
        self.assertEqual(RegistroProduccion.objects.count(), 0)

    def test_cantidad_no_numerica_se_rechaza(self):
        for valor in ["treinta", "12,5,3", "<script>"]:
            with self.subTest(cantidad=valor):
                self.registrar(cantidad=valor)
        self.assertEqual(RegistroProduccion.objects.count(), 0)

    def test_mas_de_dos_decimales_se_rechaza(self):
        self.registrar(cantidad="10.555")
        self.assertEqual(RegistroProduccion.objects.count(), 0)

    def test_fecha_futura_se_rechaza(self):
        manana = (self.hoy + timedelta(days=1)).isoformat()
        respuesta = self.registrar(fecha=manana)
        self.assertContains(respuesta, "no puede ser posterior a hoy")
        self.assertEqual(RegistroProduccion.objects.count(), 0)

    def test_fecha_con_formato_invalido_se_rechaza(self):
        for valor in ["31/02/2026", "2026-13-01", "ayer"]:
            with self.subTest(fecha=valor):
                self.registrar(fecha=valor)
        self.assertEqual(RegistroProduccion.objects.count(), 0)

    def test_material_fuera_de_la_lista_se_rechaza(self):
        self.registrar(material="Oro")
        self.assertEqual(RegistroProduccion.objects.count(), 0)

    def test_observaciones_de_mas_de_300_caracteres_se_rechazan(self):
        self.registrar(observaciones="x" * 301)
        self.assertEqual(RegistroProduccion.objects.count(), 0)

    def test_no_se_duplica_el_mismo_material_en_el_mismo_turno(self):
        self.registrar()
        respuesta = self.registrar(cantidad="10")
        self.assertContains(respuesta, "Ya existe un registro de ese material")
        self.assertEqual(RegistroProduccion.objects.count(), 1)

    def test_caracteres_especiales_en_observaciones_se_guardan_escapados(self):
        """Tildes y enes se guardan tal cual; el HTML se muestra como texto."""
        self.registrar(observaciones="Bloque Ñ-3 <b>fracturado</b> & húmedo")
        respuesta = self.client.get(reverse("produccion"))
        self.assertContains(respuesta, "Bloque Ñ-3 &lt;b&gt;fracturado&lt;/b&gt; &amp; húmedo")

    def test_eliminar_exige_post(self):
        self.registrar()
        registro = RegistroProduccion.objects.get()
        url = reverse("eliminar_produccion", args=[registro.id])
        self.assertEqual(self.client.get(url).status_code, 405)
        self.client.post(url)
        self.assertEqual(RegistroProduccion.objects.count(), 0)


class PruebasDeNavegacion(BaseConSesion):
    """Ningun enlace del menu puede quedar apuntando a "#"."""

    def test_el_menu_no_tiene_enlaces_muertos(self):
        self.iniciar_sesion()
        for nombre in ["dashboard", "clientes", "empleados", "productos",
                       "proveedores", "ventas", "produccion", "reportes"]:
            with self.subTest(pantalla=nombre):
                html = self.client.get(reverse(nombre)).content.decode()
                self.assertNotIn('href="#"', html)
                self.assertIn(reverse("produccion"), html)
                self.assertIn(reverse("reportes"), html)
