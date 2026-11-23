"""
Copias de seguridad de la base de datos de Mining Star (PostgreSQL).

Cada respaldo es un archivo .json con todos los datos del sistema, generado
con dumpdata. Se eligio JSON como formato principal porque:

- no depende del motor ni de la version de PostgreSQL;
- no necesita programas externos, asi que funciona igual en los equipos del
  equipo, en Windows y en Railway;
- se restaura con el comando restaurar_bd (flush + loaddata) dentro de una
  transaccion: si algo falla, la base queda como estaba.

Si en el equipo esta instalado pg_dump (viene con PostgreSQL), ademas se
genera una copia .dump en formato propio de PostgreSQL, que se restaura con
pg_restore. Es opcional: el .json basta para recuperar el sistema.
"""

import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.db import connection

CARPETA = Path(getattr(settings, "RESPALDOS_DIR", settings.BASE_DIR / "respaldos"))

# Tablas que no se respaldan: Django las regenera (contenttypes, permisos) o
# son temporales (sesiones, tokens de refresco ya usados).
EXCLUIDAS = ["contenttypes", "auth.permission", "sessions", "token_blacklist"]


def crear_respaldo(conservar=10, con_pg_dump=True):
    """Crea el respaldo y borra los mas antiguos. Devuelve la ruta del .json."""
    CARPETA.mkdir(parents=True, exist_ok=True)
    marca = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    destino = CARPETA / f"mining_star_{marca}.json"

    with destino.open("w", encoding="utf-8") as archivo:
        call_command(
            "dumpdata", "--natural-foreign", "--natural-primary",
            *[f"--exclude={tabla}" for tabla in EXCLUIDAS],
            "--indent=2", stdout=archivo,
        )

    if con_pg_dump:
        _copia_pg_dump(destino.with_suffix(".dump"))

    _depurar(conservar)
    return destino


def _copia_pg_dump(destino):
    """Copia nativa de PostgreSQL, solo si pg_dump esta disponible."""
    programa = shutil.which("pg_dump")
    if not programa or connection.vendor != "postgresql":
        return None
    db = settings.DATABASES["default"]
    entorno = {**os.environ, "PGPASSWORD": str(db.get("PASSWORD") or "")}
    orden = [
        programa, "--format=custom", f"--file={destino}",
        f"--host={db.get('HOST') or 'localhost'}", f"--port={db.get('PORT') or 5432}",
        f"--username={db.get('USER')}", db["NAME"],
    ]
    resultado = subprocess.run(orden, env=entorno, capture_output=True, timeout=300, check=False)
    if resultado.returncode != 0:
        destino.unlink(missing_ok=True)
        return None
    return destino


def listar_respaldos():
    if not CARPETA.exists():
        return []
    archivos = sorted(CARPETA.glob("mining_star_*.json"), reverse=True)
    return [
        {
            "archivo": a.name,
            "tamano_kb": round(a.stat().st_size / 1024, 1),
            "fecha": datetime.fromtimestamp(a.stat().st_mtime).isoformat(timespec="seconds"),
            "con_pg_dump": a.with_suffix(".dump").exists(),
        }
        for a in archivos
    ]


def _depurar(conservar):
    archivos = sorted(CARPETA.glob("mining_star_*.json"), reverse=True)
    for viejo in archivos[conservar:]:
        viejo.unlink(missing_ok=True)
        viejo.with_suffix(".dump").unlink(missing_ok=True)
