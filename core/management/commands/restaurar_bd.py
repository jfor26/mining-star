"""python manage.py restaurar_bd respaldos/mining_star_AAAAMMDD_HHMMSS_xxxxxx.sqlite3

Reemplaza la base de datos actual por un respaldo. Antes de hacerlo crea un
respaldo de seguridad del estado actual, por si el archivo elegido no era el
correcto. Detenga el servidor (runserver) antes de restaurar.
"""

import shutil
import sqlite3
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection

from core.respaldos import crear_respaldo


class Command(BaseCommand):
    help = "Restaura la base de datos desde un archivo de respaldo .sqlite3."

    def add_arguments(self, parser):
        parser.add_argument("archivo", help="Ruta del respaldo .sqlite3")
        parser.add_argument("--si", action="store_true", help="No pedir confirmacion.")

    def handle(self, *args, **opciones):
        origen = Path(opciones["archivo"])
        if not origen.exists():
            raise CommandError(f"No existe el archivo {origen}")
        try:
            with sqlite3.connect(origen) as prueba:
                if prueba.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                    raise CommandError("El respaldo esta danado (integrity_check fallo).")
        except sqlite3.DatabaseError as error:
            raise CommandError(f"El archivo no es una base SQLite valida: {error}") from error

        if not opciones["si"]:
            respuesta = input(f"Se reemplazara la base actual por {origen.name}. Escriba SI para continuar: ")
            if respuesta.strip().upper() != "SI":
                self.stdout.write("Operacion cancelada.")
                return

        previo = crear_respaldo(con_json=False, conservar=50)
        self.stdout.write(f"Estado actual guardado en {previo.name}")
        connection.close()
        shutil.copyfile(origen, settings.DATABASES["default"]["NAME"])
        self.stdout.write(self.style.SUCCESS(f"Base de datos restaurada desde {origen.name}"))
