"""
Configuracion de Django para el proyecto Mining Star.

Los valores sensibles (SECRET_KEY, DEBUG, ALLOWED_HOSTS) NO se escriben aqui:
se leen del archivo .env, que esta excluido de Git. Asi el codigo se puede
publicar sin filtrar credenciales.

Documentacion: https://docs.djangoproject.com/en/6.0/ref/settings/
"""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

# ==========================================================
# RUTAS
# ==========================================================

BASE_DIR = Path(__file__).resolve().parent.parent

# Carga las variables definidas en el archivo .env
load_dotenv(BASE_DIR / ".env")


# ==========================================================
# SEGURIDAD
# ==========================================================

# La clave se lee del entorno. Si falta, la aplicacion no arranca:
# es preferible un error claro a un despliegue inseguro silencioso.
SECRET_KEY = os.environ["DJANGO_SECRET_KEY"]

# DEBUG solo se activa si la variable dice explicitamente "True".
DEBUG = os.getenv("DJANGO_DEBUG", "False").strip().lower() == "true"

ALLOWED_HOSTS = [
    host.strip()
    for host in os.getenv("DJANGO_ALLOWED_HOSTS", "").split(",")
    if host.strip()
]

# Endurecimiento adicional que solo aplica en produccion (DEBUG = False).
if not DEBUG:
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_HSTS_SECONDS = 31_536_000          # 1 anio
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    X_FRAME_OPTIONS = "DENY"


# ==========================================================
# APLICACIONES
# ==========================================================

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.humanize",

    # Terceros: API REST
    "rest_framework",
    "django_filters",
    "drf_spectacular",

    "core",
]


# ==========================================================
# API REST
# ==========================================================
# La API exige autenticacion en todos sus puntos salvo el registro y el
# inicio de sesion: los datos de clientes y empleados son datos personales
# sujetos a la Ley 1581 de 2012.

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
    ),
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 20,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}

# Vida util de los tokens. Corta para el de acceso porque viaja en cada
# peticion; larga para el de refresco, que solo viaja al renovar.
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=2),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "API REST de Mining Star",
    "DESCRIPTION": (
        "Servicios web del sistema de gestion Mining Star, de Ortega Espinosa "
        "y Compania S.A.S. Expone la autenticacion y los cinco modulos del "
        "sistema: clientes, proveedores, productos, empleados y ventas."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"


# ==========================================================
# BASE DE DATOS
# ==========================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}


# ==========================================================
# AUTENTICACION
# ==========================================================

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# A donde redirige @login_required cuando el usuario no ha iniciado sesion.
LOGIN_URL = "login"

# A donde va el usuario despues de iniciar y cerrar sesion.
LOGIN_REDIRECT_URL = "dashboard"
LOGOUT_REDIRECT_URL = "login"

# Cierra la sesion al cerrar el navegador y la expira a las 8 horas.
SESSION_EXPIRE_AT_BROWSER_CLOSE = True
SESSION_COOKIE_AGE = 60 * 60 * 8


# ==========================================================
# INTERNACIONALIZACION
# ==========================================================

LANGUAGE_CODE = "es-co"
TIME_ZONE = "America/Bogota"
USE_I18N = True
USE_TZ = True


# ==========================================================
# ARCHIVOS ESTATICOS Y MEDIA
# ==========================================================

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Destino de "collectstatic" al desplegar.
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ==========================================================
# OTROS
# ==========================================================

# Evita el aviso models.W042 fijando el tipo de llave primaria por defecto.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
