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

import dj_database_url
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

# Origenes de confianza para formularios con CSRF (por ejemplo, el dominio
# publico de Railway). Lista separada por comas con https://.
CSRF_TRUSTED_ORIGINS = [
    origen.strip()
    for origen in os.getenv("DJANGO_CSRF_TRUSTED_ORIGINS", "").split(",")
    if origen.strip()
]

# Endurecimiento adicional que solo aplica en produccion (DEBUG = False).
if not DEBUG:
    # En Railway (y otros PaaS) el HTTPS termina en el proxy; esta cabecera
    # le indica a Django que la peticion original ya era segura.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = os.getenv("DJANGO_SSL_REDIRECT", "True").strip().lower() == "true"
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

    # Terceros: CORS para que la interfaz React publicada en otro dominio
    # pueda consumir la API (solo los origenes de DJANGO_CORS_ORIGINS).
    "corsheaders",

    # Terceros: API REST
    "rest_framework",
    # Lista negra de tokens: al cerrar sesion el token de refresco queda
    # invalidado en el servidor y no puede reutilizarse.
    "rest_framework_simplejwt.token_blacklist",
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
    # Los formularios publicos (PQRS y contacto) limitan cuantas solicitudes
    # puede enviar una misma IP, para frenar el spam.
    "DEFAULT_THROTTLE_RATES": {"publico": os.getenv("LIMITE_FORMULARIOS_PUBLICOS", "20/hour")},
}

# Vida util de los tokens. Corta para el de acceso porque viaja en cada
# peticion; larga para el de refresco, que solo viaja al renovar.
# El token de acceso se emite cada vez que un empleado entra al aplicativo.
# Rotacion: cada renovacion entrega un token de refresco nuevo y el anterior
# pasa a la lista negra, de modo que un token robado deja de servir pronto.
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=int(os.getenv("JWT_ACCESS_MINUTOS", "30"))),
    "REFRESH_TOKEN_LIFETIME": timedelta(hours=int(os.getenv("JWT_REFRESH_HORAS", "8"))),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

# Bloqueo por fuerza bruta: tras INTENTOS_MAXIMOS fallidos seguidos para un
# mismo usuario (o desde una misma IP) dentro de la ventana, se rechaza el
# ingreso hasta que pase la ventana.
LOGIN_INTENTOS_MAXIMOS = int(os.getenv("LOGIN_INTENTOS_MAXIMOS", "5"))
LOGIN_INTENTOS_MAXIMOS_POR_IP = int(os.getenv("LOGIN_INTENTOS_MAXIMOS_POR_IP", "20"))
LOGIN_VENTANA_MINUTOS = int(os.getenv("LOGIN_VENTANA_MINUTOS", "15"))

SPECTACULAR_SETTINGS = {
    "TITLE": "API REST de Mining Star Services and Products ERP",
    "DESCRIPTION": (
        "Servicios web de Mining Star Services and Products ERP, de Industrias "
        "Mineras S.A.S. Expone la autenticacion y los cinco modulos del "
        "sistema: clientes, proveedores, productos, empleados y ventas."
    ),
    "VERSION": "1.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "COMPONENT_SPLIT_REQUEST": True,
    "ENUM_NAME_OVERRIDES": {"CargoEnum": "core.models.Empleado.CARGOS"},
}

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    # Sirve los archivos estaticos en produccion sin un servidor aparte.
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
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

# Mining Star usa PostgreSQL en todos los ambientes (desarrollo, pruebas y
# produccion) para que el sistema se comporte igual en todos lados.
# La conexion llega en DATABASE_URL; en desarrollo, si no se define, se usa
# la base local que crea docker-compose.yml (ver docs/12-postgresql.md).
DATABASE_URL_LOCAL = "postgres://miningstar:miningstar@localhost:5432/miningstar"

DATABASES = {
    "default": dj_database_url.config(
        default=DATABASE_URL_LOCAL, conn_max_age=600, conn_health_checks=True
    )
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

# WhiteNoise comprime los estaticos al ejecutar collectstatic.
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "whitenoise.storage.CompressedStaticFilesStorage"},
}

# Interfaz React publicada en otro dominio (por ejemplo, Railway).
CORS_ALLOWED_ORIGINS = [
    origen.strip()
    for origen in os.getenv("DJANGO_CORS_ORIGINS", "").split(",")
    if origen.strip()
]

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ==========================================================
# PASARELA DE PAGOS (STRIPE)
# ==========================================================
# Sin STRIPE_SECRET_KEY el carrito funciona en modo "simulado" (ver
# core/pagos.py). Para pagos de prueba reales use llaves sk_test_...
STRIPE_SECRET_KEY = os.getenv("STRIPE_SECRET_KEY", "").strip()
STRIPE_WEBHOOK_SECRET = os.getenv("STRIPE_WEBHOOK_SECRET", "").strip()
STRIPE_MONEDA = os.getenv("STRIPE_MONEDA", "cop").strip().lower()
# Direccion del front-end a la que Stripe devuelve al cliente.
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173").rstrip("/")


# ==========================================================
# RESPALDOS
# ==========================================================
RESPALDOS_DIR = Path(os.getenv("RESPALDOS_DIR", BASE_DIR / "respaldos"))


# ==========================================================
# CABECERAS DE SEGURIDAD (tambien en desarrollo)
# ==========================================================
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_REFERRER_POLICY = "same-origin"
X_FRAME_OPTIONS = "DENY"
SESSION_COOKIE_HTTPONLY = True


# ==========================================================
# OTROS
# ==========================================================

# Evita el aviso models.W042 fijando el tipo de llave primaria por defecto.
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
