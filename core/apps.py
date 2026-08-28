from django.apps import AppConfig


class CoreConfig(AppConfig):
    # Fija el tipo de llave primaria para esta app y evita el aviso models.W042.
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"
    verbose_name = "Nucleo de Mining Star"
