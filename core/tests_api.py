"""
Pruebas de la API REST de Mining Star.

Cubren las dos evidencias de la actividad AA5: los servicios de registro e
inicio de sesion (EV01) y los servicios de los modulos del proyecto (EV03).

El criterio que guia estas pruebas es el mismo que el de core/tests.py: no
comprobar que el codigo hace lo que hace, sino que rechaza lo que debe
rechazar. Una API que devuelve 200 siempre es facil de escribir y no sirve.
"""

from decimal import Decimal

from django.contrib.auth.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from .models import Cliente, Producto, Proveedor, Venta


class BaseAPI(APITestCase):
    """Crea un usuario, obtiene su token y prepara datos minimos."""

    def setUp(self):
        self.usuario = User.objects.create_user(
            username="operario", email="operario@miningstar.co", password="Marmol2026*"
        )
        respuesta = self.client.post(
            reverse("api-login"),
            {"username": "operario", "password": "Marmol2026*"},
            format="json",
        )
        self.token = respuesta.data["access"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.token}")

        self.proveedor = Proveedor.objects.create(
            nit="900123456", empresa="Canteras del Tolima", contacto="Ana Ruiz",
            correo="ana@canteras.co", telefono="3001112233",
            ciudad="Ibague", direccion="Km 5 via al norte",
        )
        self.producto = Producto.objects.create(
            codigo="MAR-001", nombre="Marmol blanco 60x60", categoria="Lamina",
            proveedor=self.proveedor,
            precio_compra=Decimal("80000"), precio_venta=Decimal("185000"),
            stock=10, stock_minimo=3,
        )
        self.cliente = Cliente.objects.create(
            documento="1085123456", nombre="Constructora Andina",
            correo="compras@andina.co", telefono="3009998877", empresa="Andina S.A.S.",
        )


# ==========================================================
# EVIDENCIA AA5-EV01 — REGISTRO E INICIO DE SESION
# ==========================================================

class PruebasDeRegistro(APITestCase):

    def test_registro_valido_crea_el_usuario_y_devuelve_token(self):
        respuesta = self.client.post(reverse("api-registro"), {
            "username": "nuevo.usuario", "email": "nuevo@miningstar.co",
            "password": "Calizas2026*", "password2": "Calizas2026*",
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(respuesta.data["mensaje"], "Registro satisfactorio.")
        self.assertIn("access", respuesta.data)
        self.assertTrue(User.objects.filter(username="nuevo.usuario").exists())

    def test_la_contrasena_nunca_viaja_en_la_respuesta(self):
        respuesta = self.client.post(reverse("api-registro"), {
            "username": "otro.usuario", "email": "otro@miningstar.co",
            "password": "Calizas2026*", "password2": "Calizas2026*",
        }, format="json")
        self.assertNotIn("password", str(respuesta.data))

    def test_contrasenas_distintas_son_rechazadas(self):
        respuesta = self.client.post(reverse("api-registro"), {
            "username": "fallido", "email": "fallido@miningstar.co",
            "password": "Calizas2026*", "password2": "Otra2026*",
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("password2", respuesta.data["errores"])

    def test_contrasena_debil_es_rechazada(self):
        respuesta = self.client.post(reverse("api-registro"), {
            "username": "debil", "email": "debil@miningstar.co",
            "password": "12345678", "password2": "12345678",
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_usuario_duplicado_es_rechazado(self):
        User.objects.create_user(username="repetido", email="r@miningstar.co", password="Calizas2026*")
        respuesta = self.client.post(reverse("api-registro"), {
            "username": "repetido", "email": "distinto@miningstar.co",
            "password": "Calizas2026*", "password2": "Calizas2026*",
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("username", respuesta.data["errores"])


class PruebasDeInicioDeSesion(APITestCase):

    def setUp(self):
        User.objects.create_user(
            username="juan.ortega", email="juan@miningstar.co", password="Marmol2026*"
        )

    def test_credenciales_correctas_devuelven_autenticacion_satisfactoria(self):
        respuesta = self.client.post(reverse("api-login"), {
            "username": "juan.ortega", "password": "Marmol2026*",
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertTrue(respuesta.data["autenticado"])
        self.assertEqual(respuesta.data["mensaje"], "Autenticacion satisfactoria.")
        self.assertIn("access", respuesta.data)

    def test_contrasena_incorrecta_devuelve_error_de_autenticacion(self):
        respuesta = self.client.post(reverse("api-login"), {
            "username": "juan.ortega", "password": "equivocada",
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertFalse(respuesta.data["autenticado"])
        self.assertIn("Error en la autenticacion", respuesta.data["mensaje"])

    def test_usuario_inexistente_devuelve_el_mismo_mensaje(self):
        """No debe poder distinguirse si el usuario existe o no.

        Distinguir ambos casos permitiria averiguar por fuerza bruta que
        nombres de usuario estan registrados en el sistema.
        """
        respuesta = self.client.post(reverse("api-login"), {
            "username": "no.existe", "password": "loquesea",
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("usuario o contrasena incorrectos", respuesta.data["mensaje"])

    def test_perfil_exige_token(self):
        self.assertEqual(
            self.client.get(reverse("api-perfil")).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )


# ==========================================================
# EVIDENCIA AA5-EV03 — SERVICIOS DE LOS MODULOS
# ==========================================================

class PruebasDeAccesoALaAPI(BaseAPI):

    def test_sin_token_ningun_modulo_responde(self):
        self.client.credentials()  # retira la cabecera de autorizacion
        for ruta in ["api-clientes-list", "api-proveedores-list",
                     "api-productos-list", "api-empleados-list", "api-ventas-list"]:
            with self.subTest(ruta=ruta):
                self.assertEqual(
                    self.client.get(reverse(ruta)).status_code,
                    status.HTTP_401_UNAUTHORIZED,
                )

    def test_con_token_el_listado_responde(self):
        respuesta = self.client.get(reverse("api-clientes-list"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(respuesta.data["count"], 1)


class PruebasDeClientes(BaseAPI):

    def test_crear_cliente(self):
        respuesta = self.client.post(reverse("api-clientes-list"), {
            "documento": "1085999888", "nombre": "Marmoles del Sur",
            "correo": "info@marmolesdelsur.co", "telefono": "3157654321",
            "empresa": "Marmoles del Sur S.A.S.",
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Cliente.objects.count(), 2)

    def test_documento_no_numerico_es_rechazado(self):
        respuesta = self.client.post(reverse("api-clientes-list"), {
            "documento": "ABC123", "nombre": "Prueba",
            "correo": "p@p.co", "telefono": "300", "empresa": "Prueba",
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("documento", respuesta.data)

    def test_correo_invalido_es_rechazado(self):
        respuesta = self.client.post(reverse("api-clientes-list"), {
            "documento": "1085000111", "nombre": "Prueba",
            "correo": "esto-no-es-un-correo", "telefono": "300", "empresa": "Prueba",
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_documento_duplicado_es_rechazado(self):
        respuesta = self.client.post(reverse("api-clientes-list"), {
            "documento": self.cliente.documento, "nombre": "Otro",
            "correo": "otro@otro.co", "telefono": "300", "empresa": "Otro",
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_actualizar_y_eliminar(self):
        url = reverse("api-clientes-detail", args=[self.cliente.id])
        self.assertEqual(
            self.client.patch(url, {"telefono": "3001234567"}, format="json").status_code,
            status.HTTP_200_OK,
        )
        self.assertEqual(
            self.client.delete(url).status_code, status.HTTP_204_NO_CONTENT
        )


class PruebasDeProductos(BaseAPI):

    def test_precio_de_venta_menor_al_de_compra_es_rechazado(self):
        respuesta = self.client.post(reverse("api-productos-list"), {
            "codigo": "MAR-999", "nombre": "Lamina de prueba", "categoria": "Lamina",
            "proveedor": self.proveedor.id,
            "precio_compra": "100000", "precio_venta": "50000",
            "stock": 5, "stock_minimo": 2,
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("precio_venta", respuesta.data)

    def test_stock_negativo_es_rechazado(self):
        respuesta = self.client.post(reverse("api-productos-list"), {
            "codigo": "MAR-998", "nombre": "Lamina", "categoria": "Lamina",
            "proveedor": self.proveedor.id,
            "precio_compra": "100", "precio_venta": "200",
            "stock": -5, "stock_minimo": 2,
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_servicio_de_stock_bajo(self):
        self.producto.stock = 2
        self.producto.save(update_fields=["stock"])
        respuesta = self.client.get(reverse("api-productos-stock-bajo"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        self.assertEqual(len(respuesta.data), 1)

    def test_busqueda_por_nombre(self):
        respuesta = self.client.get(reverse("api-productos-list"), {"search": "blanco"})
        self.assertEqual(respuesta.data["count"], 1)


class PruebasDeVentasAPI(BaseAPI):

    def test_registrar_venta_descuenta_el_inventario(self):
        respuesta = self.client.post(reverse("api-ventas-registrar"), {
            "cliente": self.cliente.id, "producto": self.producto.id, "cantidad": 3,
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 7)
        self.assertEqual(
            respuesta.data["venta"]["total"], "555000.00"
        )

    def test_no_se_puede_vender_mas_de_lo_disponible(self):
        respuesta = self.client.post(reverse("api-ventas-registrar"), {
            "cliente": self.cliente.id, "producto": self.producto.id, "cantidad": 50,
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)  # el inventario no se movio

    def test_cantidad_cero_es_rechazada(self):
        respuesta = self.client.post(reverse("api-ventas-registrar"), {
            "cliente": self.cliente.id, "producto": self.producto.id, "cantidad": 0,
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anular_venta_devuelve_el_inventario(self):
        creada = self.client.post(reverse("api-ventas-registrar"), {
            "cliente": self.cliente.id, "producto": self.producto.id, "cantidad": 4,
        }, format="json")
        venta_id = creada.data["venta"]["id"]

        respuesta = self.client.post(reverse("api-ventas-anular", args=[venta_id]))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)

        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)

    def test_anular_dos_veces_no_infla_el_inventario(self):
        creada = self.client.post(reverse("api-ventas-registrar"), {
            "cliente": self.cliente.id, "producto": self.producto.id, "cantidad": 4,
        }, format="json")
        venta_id = creada.data["venta"]["id"]

        self.client.post(reverse("api-ventas-anular", args=[venta_id]))
        segunda = self.client.post(reverse("api-ventas-anular", args=[venta_id]))

        self.assertEqual(segunda.status_code, status.HTTP_400_BAD_REQUEST)
        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)  # no 14

    def test_no_se_puede_crear_una_venta_sin_pasar_por_registrar(self):
        """Un POST directo a /ventas/ crearia una venta sin detalle y sin
        descontar inventario. Solo /ventas/registrar/ puede crear ventas."""
        respuesta = self.client.post(reverse("api-ventas-list"), {
            "cliente": self.cliente.id, "estado": "Completada",
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.assertEqual(Venta.objects.count(), 0)

    def test_eliminar_venta_devuelve_el_inventario(self):
        """Borrar una venta vigente tiene que devolver sus unidades al stock,
        igual que en la aplicacion web."""
        creada = self.client.post(reverse("api-ventas-registrar"), {
            "cliente": self.cliente.id, "producto": self.producto.id, "cantidad": 4,
        }, format="json")
        venta_id = creada.data["venta"]["id"]

        respuesta = self.client.delete(reverse("api-ventas-detail", args=[venta_id]))
        self.assertEqual(respuesta.status_code, status.HTTP_204_NO_CONTENT)

        self.producto.refresh_from_db()
        self.assertEqual(self.producto.stock, 10)
        self.assertFalse(Venta.objects.filter(pk=venta_id).exists())


class PruebasDeResumen(BaseAPI):

    def test_el_resumen_entrega_los_indicadores(self):
        respuesta = self.client.get(reverse("api-resumen"))
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
        for clave in ["clientes", "proveedores", "productos", "empleados",
                      "ventas", "total_vendido", "productos_stock_bajo"]:
            self.assertIn(clave, respuesta.data)
        self.assertEqual(respuesta.data["clientes"], 1)


class PruebasDeDocumentacion(BaseAPI):

    def test_el_esquema_openapi_se_genera(self):
        respuesta = self.client.get("/api/schema/")
        self.assertEqual(respuesta.status_code, status.HTTP_200_OK)
