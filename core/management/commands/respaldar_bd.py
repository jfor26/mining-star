"""python manage.py respaldar_bd [--conservar 10]

Crea una copia de seguridad de la base de datos en respaldos/.
En Windows se puede programar con el Programador de tareas usando
scripts/respaldo_diario.bat.
"""

from django.core.management.base import BaseCommand

from core.respaldos import crear_respaldo


class Command(BaseCommand):
    help = "Crea una copia de seguridad de la base de datos (.json y, si hay pg_dump, .dump)."

    def add_arguments(self, parser):
        parser.add_argument("--conservar", type=int, default=10,
                            help="Cuantos respaldos mantener (los mas antiguos se borran).")
        parser.add_argument("--sin-pg-dump", action="store_true", help="No generar la copia .dump de PostgreSQL.")

    def handle(self, *args, **opciones):
        ruta = crear_respaldo(conservar=opciones["conservar"], con_pg_dump=not opciones["sin_pg_dump"])
        self.stdout.write(self.style.SUCCESS(f"Respaldo creado: {ruta}"))
