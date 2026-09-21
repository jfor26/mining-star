"""
Rutas raiz del proyecto Mining Star.

Tres bloques: el administrador de Django, la API REST versionada y la
aplicacion web. La documentacion de la API se publica junto a ella para que
no pueda quedar desactualizada respecto del codigo: se genera a partir de
los propios serializadores y vistas.
"""

from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)

urlpatterns = [
    path("admin/", admin.site.urls),

    # API REST
    path("api/v1/", include("core.api.urls")),

    # Documentacion de la API
    path("api/schema/", SpectacularAPIView.as_view(), name="esquema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="esquema"), name="docs"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="esquema"), name="redoc"),

    # Aplicacion web
    path("", include("core.urls")),
]
