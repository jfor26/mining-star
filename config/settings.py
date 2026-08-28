"""
Configuracion de Django para el proyecto Mining Star.

Los valores sensibles (SECRET_KEY, DEBUG, ALLOWED_HOSTS) NO se escriben aqui:
se leen del archivo .env, que esta excluido de Git. Asi el codigo se puede
publicar sin filtrar credenciales.

Documentacion: https://docs.djangoproject.com/en/6.0/ref/settings/
"""

import os
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
    "core",
]

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
