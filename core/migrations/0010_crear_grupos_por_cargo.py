"""Crea un grupo de Django por cada cargo de la matriz de acceso.

Se hace en una migracion de datos para que cualquier instalacion nueva
(o la base de pruebas) tenga los roles sin pasos manuales.
"""

from django.db import migrations

ROLES = ["Administrador", "Gerente", "Supervisor", "Comercial", "Contador", "Operario", "Auxiliar"]


def crear_grupos(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    for rol in ROLES:
        Group.objects.get_or_create(name=rol)


def borrar_grupos(apps, schema_editor):
    apps.get_model("auth", "Group").objects.filter(name__in=ROLES).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("auth", "0012_alter_user_first_name_max_length"),
        ("core", "0009_seguridad_crm_tienda_normativa_mejora"),
    ]

    operations = [migrations.RunPython(crear_grupos, borrar_grupos)]
