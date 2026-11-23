# Respaldo (backup) y restauración

| Forma | Cómo |
|---|---|
| Desde el aplicativo | *Seguridad → Respaldos (backup) → Crear respaldo ahora* (solo Administrador) |
| Desde la terminal | `python manage.py respaldar_bd` |
| Automático diario (Windows) | Programador de tareas → *Crear tarea básica* → Diariamente → Iniciar un programa → `scripts\respaldo_diario.bat` |

Cada respaldo crea en `respaldos/`:
- `mining_star_AAAAMMDD_HHMMSS_xxxxxx.json` (`dumpdata`): todos los datos en formato portable; es el respaldo principal;
- el mismo nombre en `.dump`, solo si el equipo tiene `pg_dump` (viene con PostgreSQL): copia nativa que se restaura con `pg_restore`.

Se conservan los 10 más recientes (`--conservar N` para cambiarlo). La carpeta está en `.gitignore` porque contiene datos personales: **copie los respaldos a OneDrive u otro disco**, no a GitHub.

## Restaurar

```bash
# 1. Detener el servidor (Ctrl + C en la terminal de runserver)
# 2. Restaurar; antes de reemplazar, guarda una copia del estado actual
python manage.py restaurar_bd respaldos/mining_star_20261006_230000_000000.json
# 3. Escribir SI para confirmar y volver a levantar el servidor
```

El comando verifica que el archivo sea un JSON válido y hace la carga dentro de una transacción: si algo falla, la base queda como estaba. Detalles de PostgreSQL en `docs/12-postgresql.md`.
