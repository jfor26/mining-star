"""
Copias de seguridad de la base de datos de Mining Star.

Se usa la API de respaldo de SQLite (sqlite3.Connection.backup) y no una
simple copia del archivo: copiar db.sqlite3 mientras alguien escribe puede
producir un archivo corrupto, mientras que la API de respaldo hace una copia
consistente aunque el servidor siga atendiendo usuarios.

Ademas del archivo .sqlite3 se exporta un .json con dumpdata: si algun dia
se migra a PostgreSQL, ese JSON se carga con loaddata.
"""

import sqlite3
from datetime import datetime
from io import StringIO
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.db import connection

CARPETA = Path(getattr(settings, "RESPALDOS_DIR", settings.BASE_DIR / "respaldos"))


def crear_respaldo(conservar=10, con_json=True):
    """Crea el respaldo y borra los mas antiguos. Devuelve la ruta creada."""
    CARPETA.mkdir(parents=True, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    destino = CARPETA / f"mining_star_{marca}.sqlite3"

    if connection.vendor != "sqlite":
        raise RuntimeError("El respaldo binario solo aplica a SQLite; use pg_dump en PostgreSQL.")

    connection.ensure_connection()
    with sqlite3.connect(destino) as copia:
        connection.connection.backup(copia)

    if con_json:
        salida = StringIO()
        call_command(
            "dumpdata", "--natural-foreign", "--natural-primary",
            "--exclude=contenttypes", "--exclude=auth.permission",
            "--exclude=sessions", "--exclude=token_blacklist",
            "--indent=2", stdout=salida,
        )
        destino.with_suffix(".json").write_text(salida.getvalue(), encoding="utf-8")

    _depurar(conservar)
    return destino


def listar_respaldos():
    if not CARPETA.exists():
        return []
    archivos = sorted(CARPETA.glob("mining_star_*.sqlite3"), reverse=True)
    return [
        {
            "archivo": a.name,
            "tamano_kb": round(a.stat().st_size / 1024, 1),
            "fecha": datetime.fromtimestamp(a.stat().st_mtime).isoformat(timespec="seconds"),
            "con_json": a.with_suffix(".json").exists(),
        }
        for a in archivos
    ]


def _depurar(conservar):
    archivos = sorted(CARPETA.glob("mining_star_*.sqlite3"), reverse=True)
    for viejo in archivos[conservar:]:
        viejo.unlink(missing_ok=True)
        viejo.with_suffix(".json").unlink(missing_ok=True)
