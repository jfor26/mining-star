"""
Rutas de la API REST de Mining Star.

Todas cuelgan de /api/v1/. El numero de version en la ruta permite publicar
una version 2 en el futuro sin romper a los clientes que ya consumen la
primera, que es la razon por la que se incluye desde el principio.
"""

from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView, TokenVerifyView

from .views import (
    ClienteViewSet,
    EmpleadoViewSet,
    LoginView,
    PerfilView,
    ProductoViewSet,
    ProveedorViewSet,
    RegistroView,
    ResumenView,
    VentaViewSet,
)

router = DefaultRouter()
router.register("clientes", ClienteViewSet, basename="api-clientes")
router.register("proveedores", ProveedorViewSet, basename="api-proveedores")
router.register("productos", ProductoViewSet, basename="api-productos")
router.register("empleados", EmpleadoViewSet, basename="api-empleados")
router.register("ventas", VentaViewSet, basename="api-ventas")

urlpatterns = [
    # Autenticacion (evidencia AA5-EV01)
    path("auth/registro/", RegistroView.as_view(), name="api-registro"),
    path("auth/login/", LoginView.as_view(), name="api-login"),
    path("auth/refrescar/", TokenRefreshView.as_view(), name="api-refrescar"),
    path("auth/verificar/", TokenVerifyView.as_view(), name="api-verificar"),
    path("auth/perfil/", PerfilView.as_view(), name="api-perfil"),

    # Panel
    path("resumen/", ResumenView.as_view(), name="api-resumen"),

    # Modulos del proyecto (evidencia AA5-EV03)
    path("", include(router.urls)),
]
