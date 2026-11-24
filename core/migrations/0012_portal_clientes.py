"""Portal de clientes: cuenta del cliente, origen de la oportunidad y grupo Cliente."""

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


def crear_grupo(apps, schema_editor):
    apps.get_model("auth", "Group").objects.get_or_create(name="Cliente")


def borrar_grupo(apps, schema_editor):
    apps.get_model("auth", "Group").objects.filter(name="Cliente").delete()


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("core", "0011_notificacion_leida"),
    ]

    operations = [
        migrations.AddField(
            model_name="cliente",
            name="usuario",
            field=models.OneToOneField(
                blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL,
                related_name="cliente", to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="oportunidad",
            name="origen",
            field=models.CharField(
                choices=[("Interno", "Registrada por el equipo"), ("Portal", "Solicitud desde el portal")],
                default="Interno", max_length=8,
            ),
        ),
        migrations.AlterField(
            model_name="interaccion",
            name="tipo",
            field=models.CharField(
                choices=[("Llamada", "Llamada"), ("Correo", "Correo"), ("Visita", "Visita"),
                         ("Reunion", "Reunión"), ("WhatsApp", "WhatsApp"), ("Portal", "Portal de clientes")],
                max_length=10,
            ),
        ),
        migrations.RunPython(crear_grupo, borrar_grupo),
    ]
