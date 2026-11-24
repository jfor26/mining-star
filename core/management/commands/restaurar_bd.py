"""python manage.py restaurar_bd respaldos/mining_star_AAAAMMDD_HHMMSS_xxxxxx.json

Reemplaza los datos actuales por los de un respaldo .json. Antes de hacerlo
crea un respaldo del estado actual, por si el archivo elegido no era el
correcto. Todo ocurre en una transaccion: si la carga falla, la base de datos
queda exactamente como estaba.

(Las copias .dump se restauran con la herramienta de PostgreSQL:
 pg_restore --clean --dbname=<base> archivo.dump)
"""

import json
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction

from core.respaldos import crear_respaldo


class Command(BaseCommand):
    help = "Restaura la base de datos desde un respaldo .json."

    def add_arguments(self, parser):
        parser.add_argument("archivo", help="Ruta del respaldo .json")
        parser.add_argument("--si", action="store_true", help="No pedir confirmacion.")

    def handle(self, *args, **opciones):
        origen = Path(opciones["archivo"])
        if not origen.exists():
            raise CommandError(f"No existe el archivo {origen}")
        if origen.suffix != ".json":
            raise CommandError("Indique el archivo .json del respaldo.")
        try:
            registros = json.loads(origen.read_text(encoding="utf-8"))
        except (ValueError, UnicodeDecodeError) as error:
            raise CommandError(f"El respaldo esta danado o no es JSON valido: {error}") from error
        if not isinstance(registros, list):
            raise CommandError("El archivo no tiene el formato de un respaldo de Mining Star.")

        if not opciones["si"]:
            respuesta = input(f"Se reemplazaran los datos actuales por {origen.name}. Escriba SI para continuar: ")
            if respuesta.strip().upper() != "SI":
                self.stdout.write("Operacion cancelada.")
                return

        previo = crear_respaldo(conservar=50, con_pg_dump=False)
        self.stdout.write(f"Estado actual guardado en {previo.name}")

        with transaction.atomic():
            if connection.vendor == "postgresql":
                # Las llaves foraneas de PostgreSQL se verifican al final de la
                # transaccion; se fuerzan antes para que TRUNCATE no falle.
                with connection.cursor() as cursor:
                    cursor.execute("SET CONSTRAINTS ALL IMMEDIATE")
            call_command("flush", "--no-input", verbosity=0)
            call_command("loaddata", str(origen), verbosity=0)
        self.stdout.write(self.style.SUCCESS(
            f"Base de datos restaurada desde {origen.name} ({len(registros)} registros)."
        ))
