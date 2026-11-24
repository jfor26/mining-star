"""
Rutas de la API REST de Mining Star.

Todas cuelgan de /api/v1/. El numero de version en la ruta permite publicar
una version 2 en el futuro sin romper a los clientes que ya consumen la
primera, que es la razon por la que se incluye desde el principio.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .portal import CatalogoPortalView, ComprobantePortalView, CotizacionPortalView, ResumenPortalView
from .views import (
    AccionMejoraViewSet,
    ClienteViewSet,
    ConfigPagosView,
    DashboardView,
    EmpleadoViewSet,
    InteraccionViewSet,
    LoginView,
    LogoutView,
    MatrizAccesoView,
    NotificacionesView,
    OportunidadViewSet,
    PedidoViewSet,
    PerfilView,
    ProduccionViewSet,
    ProductoViewSet,
    ProveedorViewSet,
    RefrescarTokenView,
    RegistroAccesoViewSet,
    RegistroView,
    RequisitoNormativoViewSet,
    RespaldoView,
    ResumenView,
    StripeWebhookView,
    UsuarioViewSet,
    VentaViewSet,
    VerificarTokenView,
)

router = DefaultRouter()
router.register("clientes", ClienteViewSet, basename="api-clientes")
router.register("proveedores", ProveedorViewSet, basename="api-proveedores")
router.register("productos", ProductoViewSet, basename="api-productos")
router.register("empleados", EmpleadoViewSet, basename="api-empleados")
router.register("ventas", VentaViewSet, basename="api-ventas")
router.register("produccion", ProduccionViewSet, basename="api-produccion")
router.register("crm/oportunidades", OportunidadViewSet, basename="api-oportunidades")
router.register("crm/interacciones", InteraccionViewSet, basename="api-interacciones")
router.register("pedidos", PedidoViewSet, basename="api-pedidos")
router.register("normativa", RequisitoNormativoViewSet, basename="api-normativa")
router.register("mejora", AccionMejoraViewSet, basename="api-mejora")
router.register("seguridad/usuarios", UsuarioViewSet, basename="api-usuarios")
router.register("seguridad/accesos", RegistroAccesoViewSet, basename="api-accesos")

urlpatterns = [
    # Autenticacion (evidencia AA5-EV01)
    path("auth/registro/", RegistroView.as_view(), name="api-registro"),
    path("auth/login/", LoginView.as_view(), name="api-login"),
    path("auth/refrescar/", RefrescarTokenView.as_view(), name="api-refrescar"),
    path("auth/verificar/", VerificarTokenView.as_view(), name="api-verificar"),
    path("auth/perfil/", PerfilView.as_view(), name="api-perfil"),
    path("auth/logout/", LogoutView.as_view(), name="api-logout"),

    # Seguridad, pagos y tablero
    path("seguridad/matriz/", MatrizAccesoView.as_view(), name="api-matriz"),
    path("seguridad/respaldos/", RespaldoView.as_view(), name="api-respaldos"),
    path("pagos/config/", ConfigPagosView.as_view(), name="api-pagos-config"),
    path("pagos/webhook/", StripeWebhookView.as_view(), name="api-stripe-webhook"),
    path("dashboard/", DashboardView.as_view(), name="api-dashboard"),
    path("notificaciones/", NotificacionesView.as_view(), name="api-notificaciones"),
    path("portal/resumen/", ResumenPortalView.as_view(), name="api-portal-resumen"),
    path("portal/catalogo/", CatalogoPortalView.as_view(), name="api-portal-catalogo"),
    path("portal/cotizaciones/", CotizacionPortalView.as_view(), name="api-portal-cotizaciones"),
    path("portal/compras/<int:pk>/comprobante/", ComprobantePortalView.as_view(), name="api-portal-comprobante"),

    # Panel
    path("resumen/", ResumenView.as_view(), name="api-resumen"),

    # Modulos del proyecto (evidencia AA5-EV03)
    path("", include(router.urls)),
]
