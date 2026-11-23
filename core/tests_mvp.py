"""
Pruebas de los modulos agregados para el producto minimo viable.

Siguen el criterio del resto del proyecto: probar sobre todo lo que el
sistema debe RECHAZAR (un cargo sin permiso, un pago falso, un intento de
fuerza bruta), porque eso es lo que falla en silencio si nadie lo prueba.

Ejecutar solo estas pruebas:  python manage.py test core.tests_mvp
"""

import json
import shutil
import tempfile
from datetime import timedelta
from decimal import Decimal
from io import StringIO
from pathlib import Path
from unittest import mock

from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from .models import (
    AccionMejora,
    Cliente,
    Oportunidad,
    Pedido,
    Producto,
    Proveedor,
    RegistroAcceso,
    RequisitoNormativo,
    Venta,
)
from .permisos import MATRIZ_DE_ACCESO, puede, rol_de

CLAVE = "Caliza2026*Segura"


def crear_usuario(nombre, rol=None):
    usuario = User.objects.create_user(username=nombre, password=CLAVE, email=f"{nombre}@ms.example")
    if rol:
        usuario.groups.add(Group.objects.get(name=rol))
    return usuario


class DatosBase(APITestCase):
    def setUp(self):
        self.proveedor = Proveedor.objects.create(
            nit="900111222", empresa="Trituradora Andina", contacto="Mario",
            correo="m@t.example", telefono="3001112233", ciudad="Ibague", direccion="Km 2",
        )
        self.cal = Producto.objects.create(
            codigo="CAL-002", nombre="Cal agricola", categoria="Cal agricola",
            proveedor=self.proveedor, precio_compra=Decimal("9000"),
            precio_venta=Decimal("18500"), stock=20, stock_minimo=2,
        )
        self.rajon = Producto.objects.create(
            codigo="RAJ-001", nombre="Rajon", categoria="Cantera",
            proveedor=self.proveedor, precio_compra=Decimal("15000"),
            precio_venta=Decimal("24000"), stock=50, stock_minimo=5,
        )
        self.cliente = Cliente.objects.create(
            documento="900500001", nombre="Constructora Vias", correo="c@v.example",
            telefono="3200000000", empresa="Obra civil",
        )

    def entrar(self, nombre, rol):
        usuario = crear_usuario(nombre, rol)
        self.client.force_authenticate(usuario)
        return usuario


# ==========================================================
# ROLES Y PERMISOS POR CARGO
# ==========================================================

class PruebasMatrizDeAcceso(TestCase):

    def test_existe_un_grupo_por_cada_cargo(self):
        for rol in MATRIZ_DE_ACCESO:
            with self.subTest(rol=rol):
                self.assertTrue(Group.objects.filter(name=rol).exists())

    def test_usuario_sin_cargo_no_puede_nada(self):
        usuario = crear_usuario("sin.cargo")
        self.assertIsNone(rol_de(usuario))
        self.assertFalse(puede(usuario, "panel"))

    def test_superusuario_es_administrador(self):
        admin = User.objects.create_superuser("root", "r@ms.example", CLAVE)
        self.assertEqual(rol_de(admin), "Administrador")
        self.assertTrue(puede(admin, "seguridad", "eliminar"))


class PruebasPermisosEnLaAPI(DatosBase):

    def test_operario_no_ve_clientes_ni_ventas(self):
        self.entrar("op", "Operario")
        for ruta in ["api-clientes-list", "api-ventas-list", "api-oportunidades-list"]:
            with self.subTest(ruta=ruta):
                self.assertEqual(self.client.get(reverse(ruta)).status_code, status.HTTP_403_FORBIDDEN)

    def test_operario_si_registra_produccion(self):
        self.entrar("op", "Operario")
        respuesta = self.client.post(reverse("api-produccion-list"), {
            "fecha": timezone.localdate().isoformat(), "turno": "Manana",
            "material": "Caliza", "cantidad": "35", "unidad": "t",
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_201_CREATED)

    def test_operario_no_puede_borrar_produccion(self):
        self.entrar("op", "Operario")
        creado = self.client.post(reverse("api-produccion-list"), {
            "fecha": timezone.localdate().isoformat(), "turno": "Tarde",
            "material": "Marmol", "cantidad": "10", "unidad": "t",
        }, format="json").data
        respuesta = self.client.delete(reverse("api-produccion-detail", args=[creado["id"]]))
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_comercial_crea_clientes_pero_no_los_elimina(self):
        self.entrar("com", "Comercial")
        self.assertEqual(self.client.get(reverse("api-clientes-list")).status_code, 200)
        respuesta = self.client.delete(reverse("api-clientes-detail", args=[self.cliente.pk]))
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)
        self.assertTrue(Cliente.objects.filter(pk=self.cliente.pk).exists())

    def test_contador_puede_anular_pero_no_registrar_ventas(self):
        self.entrar("cont", "Contador")
        respuesta = self.client.post(reverse("api-ventas-registrar"), {
            "cliente": self.cliente.pk, "producto": self.cal.pk, "cantidad": 1,
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_perfil_devuelve_cargo_y_permisos(self):
        self.entrar("sup", "Supervisor")
        datos = self.client.get(reverse("api-perfil")).data
        self.assertEqual(datos["rol"], "Supervisor")
        self.assertIn("crear", datos["permisos"]["produccion"])
        self.assertNotIn("ventas", datos["permisos"])

    def test_solo_el_administrador_registra_usuarios(self):
        self.entrar("ger", "Gerente")
        respuesta = self.client.post(reverse("api-registro"), {
            "username": "nuevo", "email": "n@ms.example", "rol": "Administrador",
            "password": CLAVE, "password2": CLAVE,
        }, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_403_FORBIDDEN)

    def test_administrador_cambia_el_cargo_de_otro_usuario(self):
        self.entrar("adm", "Administrador")
        otro = crear_usuario("otro", "Operario")
        respuesta = self.client.post(
            reverse("api-usuarios-cambiar-rol", args=[otro.pk]), {"rol": "Supervisor"}, format="json"
        )
        self.assertEqual(respuesta.status_code, 200)
        self.assertEqual(rol_de(otro), "Supervisor")

    def test_nadie_se_cambia_su_propio_cargo(self):
        admin = self.entrar("adm", "Administrador")
        respuesta = self.client.post(
            reverse("api-usuarios-cambiar-rol", args=[admin.pk]), {"rol": "Operario"}, format="json"
        )
        self.assertEqual(respuesta.status_code, status.HTTP_400_BAD_REQUEST)

    def test_dashboard_solo_incluye_lo_que_el_cargo_puede_ver(self):
        self.entrar("op", "Operario")
        datos = self.client.get(reverse("api-dashboard")).data
        self.assertIn("produccion_diaria", datos)
        self.assertNotIn("ventas_por_mes", datos)
        self.assertNotIn("total_vendido", datos["indicadores"])


class PruebasPermisosEnLaWeb(TestCase):
    """La interfaz de plantillas Django respeta la misma matriz."""

    def test_operario_recibe_403_en_clientes(self):
        crear_usuario("op", "Operario")
        self.client.login(username="op", password=CLAVE)
        self.assertEqual(self.client.get(reverse("clientes")).status_code, 403)


# ==========================================================
# TOKEN DE ACCESO, BITACORA Y FUERZA BRUTA
# ==========================================================

class PruebasDeTokenYAccesos(APITestCase):

    def setUp(self):
        self.usuario = crear_usuario("juan", "Comercial")

    def login(self, clave=CLAVE, nombre="juan"):
        return self.client.post(reverse("api-login"), {"username": nombre, "password": clave}, format="json")

    def test_cada_ingreso_emite_token_y_queda_registrado(self):
        respuesta = self.login()
        self.assertEqual(respuesta.status_code, 200)
        registro = RegistroAcceso.objects.get(evento="ingreso")
        self.assertEqual(registro.usuario, self.usuario)
        self.assertEqual(len(registro.token_jti), 32)
        self.assertEqual(respuesta.data["usuario"]["rol"], "Comercial")

    def test_dos_ingresos_dan_tokens_distintos(self):
        primero, segundo = self.login().data["access"], self.login().data["access"]
        self.assertNotEqual(primero, segundo)

    def test_intento_fallido_queda_registrado(self):
        self.login(clave="mala")
        self.assertEqual(RegistroAcceso.objects.filter(evento="fallido", nombre_usuario="juan").count(), 1)

    @override_settings(LOGIN_INTENTOS_MAXIMOS=3)
    def test_bloqueo_tras_varios_fallos_aun_con_la_clave_correcta(self):
        for _ in range(3):
            self.login(clave="mala")
        respuesta = self.login()
        self.assertEqual(respuesta.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
        self.assertNotIn("access", respuesta.data)

    def test_cerrar_sesion_invalida_el_token_de_refresco(self):
        datos = self.login().data
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {datos['access']}")
        self.assertEqual(self.client.post(reverse("api-logout"), {"refresh": datos["refresh"]}, format="json").status_code, 200)
        self.client.credentials()
        respuesta = self.client.post(reverse("api-refrescar"), {"refresh": datos["refresh"]}, format="json")
        self.assertEqual(respuesta.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_el_refresco_rota_el_token(self):
        refresh = self.login().data["refresh"]
        nuevo = self.client.post(reverse("api-refrescar"), {"refresh": refresh}, format="json").data
        self.assertIn("refresh", nuevo)
        reuso = self.client.post(reverse("api-refrescar"), {"refresh": refresh}, format="json")
        self.assertEqual(reuso.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_operario_no_consulta_la_bitacora(self):
        operario = crear_usuario("op", "Operario")
        self.client.force_authenticate(operario)
        self.assertEqual(self.client.get(reverse("api-accesos-list")).status_code, 403)


# ==========================================================
# CRM
# ==========================================================

class PruebasCRM(DatosBase):

    def test_comercial_crea_oportunidad_y_se_calcula_el_valor_ponderado(self):
        self.entrar("com", "Comercial")
        respuesta = self.client.post(reverse("api-oportunidades-list"), {
            "cliente": self.cliente.pk, "titulo": "Rajon para via", "etapa": "Cotizacion",
            "valor_estimado": "10000000",
        }, format="json")
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(respuesta.data["probabilidad"], 50)
        self.assertEqual(Decimal(respuesta.data["valor_ponderado"]), Decimal("5000000.00"))

    def test_interaccion_no_puede_apuntar_a_oportunidad_de_otro_cliente(self):
        self.entrar("com", "Comercial")
        otro = Cliente.objects.create(documento="111", nombre="Otro", correo="o@o.example",
                                      telefono="3000000000", empresa="X")
        oportunidad = Oportunidad.objects.create(cliente=otro, titulo="X", valor_estimado=1)
        respuesta = self.client.post(reverse("api-interacciones-list"), {
            "cliente": self.cliente.pk, "oportunidad": oportunidad.pk, "tipo": "Llamada",
            "descripcion": "Prueba",
        }, format="json")
        self.assertEqual(respuesta.status_code, 400)


# ==========================================================
# CARRITO, PEDIDOS Y PAGOS
# ==========================================================

class PruebasTienda(DatosBase):

    def crear_pedido(self, items):
        return self.client.post(reverse("api-pedidos-list"), {"cliente": self.cliente.pk, "items": items}, format="json")

    def test_crear_pedido_no_descuenta_inventario(self):
        self.entrar("com", "Comercial")
        respuesta = self.crear_pedido([{"producto": self.cal.pk, "cantidad": 5}])
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(Decimal(respuesta.data["total"]), Decimal("92500"))
        self.cal.refresh_from_db()
        self.assertEqual(self.cal.stock, 20)

    def test_carrito_vacio_o_sin_stock_es_rechazado(self):
        self.entrar("com", "Comercial")
        self.assertEqual(self.crear_pedido([]).status_code, 400)
        self.assertEqual(self.crear_pedido([{"producto": self.cal.pk, "cantidad": 21}]).status_code, 400)

    @override_settings(STRIPE_SECRET_KEY="")
    def test_pago_simulado_crea_la_venta_y_descuenta_una_sola_vez(self):
        self.entrar("com", "Comercial")
        pedido = self.crear_pedido([{"producto": self.cal.pk, "cantidad": 5},
                                    {"producto": self.rajon.pk, "cantidad": 2}]).data
        url = reverse("api-pedidos-confirmar-simulado", args=[pedido["id"]])
        self.assertEqual(self.client.post(url).data["estado"], "Pagado")
        self.client.post(url)  # segundo aviso del mismo pago
        self.cal.refresh_from_db()
        self.rajon.refresh_from_db()
        self.assertEqual((self.cal.stock, self.rajon.stock), (15, 48))
        self.assertEqual(Venta.objects.count(), 1)
        self.assertEqual(Venta.objects.get().total, Decimal("140500"))

    @override_settings(STRIPE_SECRET_KEY="sk_test_falsa", FRONTEND_URL="http://localhost:5173")
    def test_con_stripe_se_crea_sesion_de_checkout(self):
        self.entrar("com", "Comercial")
        pedido = self.crear_pedido([{"producto": self.cal.pk, "cantidad": 2}]).data
        sesion = mock.Mock(id="cs_test_123", url="https://checkout.stripe.com/c/pay/cs_test_123")
        with mock.patch("stripe.checkout.Session.create", return_value=sesion) as crear:
            respuesta = self.client.post(reverse("api-pedidos-pagar", args=[pedido["id"]]))
        self.assertEqual(respuesta.data["url"], sesion.url)
        linea = crear.call_args.kwargs["line_items"][0]
        self.assertEqual(linea["price_data"]["unit_amount"], 1850000)  # $18.500 COP en centavos
        self.assertEqual(Pedido.objects.get(pk=pedido["id"]).referencia_pago, "cs_test_123")

    @override_settings(STRIPE_SECRET_KEY="sk_test_falsa")
    def test_con_stripe_el_pago_simulado_esta_prohibido(self):
        self.entrar("com", "Comercial")
        pedido = self.crear_pedido([{"producto": self.cal.pk, "cantidad": 2}]).data
        respuesta = self.client.post(reverse("api-pedidos-confirmar-simulado", args=[pedido["id"]]))
        self.assertEqual(respuesta.status_code, 403)

    @override_settings(STRIPE_SECRET_KEY="sk_test_falsa", STRIPE_WEBHOOK_SECRET="whsec_prueba")
    def test_webhook_con_firma_falsa_es_rechazado(self):
        respuesta = self.client.post(
            reverse("api-stripe-webhook"), data='{"type": "checkout.session.completed"}',
            content_type="application/json", HTTP_STRIPE_SIGNATURE="t=1,v1=falsa",
        )
        self.assertEqual(respuesta.status_code, 400)

    def test_operario_no_accede_a_la_tienda(self):
        self.entrar("op", "Operario")
        self.assertEqual(self.crear_pedido([{"producto": self.cal.pk, "cantidad": 1}]).status_code, 403)


# ==========================================================
# NORMATIVA Y MEJORA CONTINUA
# ==========================================================

class PruebasNormativaYMejora(DatosBase):

    def test_alerta_de_vencimiento(self):
        hoy = timezone.localdate()
        base = {"autoridad": "ANM", "categoria": "Minero", "norma": "Ley 685 de 2001", "descripcion": "x"}
        vencido = RequisitoNormativo.objects.create(nombre="A", fecha_vencimiento=hoy - timedelta(days=1), **base)
        proximo = RequisitoNormativo.objects.create(nombre="B", fecha_vencimiento=hoy + timedelta(days=10), **base)
        cumplido = RequisitoNormativo.objects.create(nombre="C", estado="Cumplido",
                                                     fecha_vencimiento=hoy - timedelta(days=1), **base)
        self.assertEqual((vencido.alerta, proximo.alerta, cumplido.alerta), ("vencido", "proximo", "ok"))

    def test_no_se_cierra_una_accion_sin_verificar_eficacia(self):
        self.entrar("sup", "Supervisor")
        respuesta = self.client.post(reverse("api-mejora-list"), {
            "titulo": "Polvo en via", "origen": "Ambiental", "descripcion": "Queja", "fase": "Cerrada",
        }, format="json")
        self.assertEqual(respuesta.status_code, 400)
        self.assertIn("resultado", respuesta.data)

    def test_operario_propone_mejoras(self):
        self.entrar("op", "Operario")
        respuesta = self.client.post(reverse("api-mejora-list"), {
            "titulo": "Señalizar zona de cargue", "origen": "Empleado", "descripcion": "Sugerencia",
        }, format="json")
        self.assertEqual(respuesta.status_code, 201)
        self.assertEqual(AccionMejora.objects.get().creado_por.username, "op")


# ==========================================================
# RESPALDOS Y DATOS DE DEMOSTRACION
# ==========================================================

class PruebasDeRespaldo(TestCase):

    def setUp(self):
        self.carpeta = Path(tempfile.mkdtemp())
        parche = mock.patch("core.respaldos.CARPETA", self.carpeta)
        parche.start()
        self.addCleanup(parche.stop)
        self.addCleanup(shutil.rmtree, self.carpeta, ignore_errors=True)

    def test_el_comando_crea_respaldo_json(self):
        call_command("respaldar_bd", "--sin-pg-dump", stdout=StringIO())
        archivos = list(self.carpeta.glob("*.json"))
        self.assertEqual(len(archivos), 1)
        datos = json.loads(archivos[0].read_text(encoding="utf-8"))
        self.assertTrue(any(r["model"] == "auth.group" for r in datos))

    def test_solo_conserva_los_ultimos_respaldos(self):
        from .respaldos import crear_respaldo
        for _ in range(4):
            crear_respaldo(conservar=2, con_pg_dump=False)
        self.assertEqual(len(list(self.carpeta.glob("*.json"))), 2)

    def test_restaurar_devuelve_los_datos_del_respaldo(self):
        from .respaldos import crear_respaldo
        Cliente.objects.create(documento="555", nombre="Antes", correo="a@b.co",
                               telefono="3000000000", empresa="X")
        ruta = crear_respaldo(con_pg_dump=False)
        Cliente.objects.create(documento="556", nombre="Despues", correo="c@d.co",
                               telefono="3000000001", empresa="Y")
        call_command("restaurar_bd", str(ruta), "--si", stdout=StringIO())
        self.assertTrue(Cliente.objects.filter(documento="555").exists())
        self.assertFalse(Cliente.objects.filter(documento="556").exists())

    def test_restaurar_rechaza_un_archivo_danado(self):
        malo = self.carpeta / "malo.json"
        malo.write_text("{no es json", encoding="utf-8")
        with self.assertRaises(CommandError):
            call_command("restaurar_bd", str(malo), "--si", stdout=StringIO())

    def test_solo_seguridad_lista_respaldos_por_api(self):
        usuario = crear_usuario("op", "Operario")
        cliente = APIClient()
        cliente.force_authenticate(usuario)
        self.assertEqual(cliente.get(reverse("api-respaldos")).status_code, 403)


class PruebasDatosDeDemostracion(TestCase):

    def test_cargar_demo_es_idempotente_y_crea_un_usuario_por_cargo(self):
        call_command("cargar_demo", clave=CLAVE, stdout=StringIO())
        call_command("cargar_demo", clave=CLAVE, stdout=StringIO())
        for nombre, rol in [("gerente", "Gerente"), ("operario", "Operario"), ("admin.ms", "Administrador")]:
            self.assertEqual(rol_de(User.objects.get(username=nombre)), rol)
        self.assertEqual(Producto.objects.filter(codigo="RAJ-001").count(), 1)
        self.assertGreater(Venta.objects.count(), 20)

    def test_cargar_demo_rechaza_claves_debiles(self):
        from django.core.management.base import CommandError
        with self.assertRaises(CommandError):
            call_command("cargar_demo", clave="123")
