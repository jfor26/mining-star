# Mining Star con PostgreSQL

Desde la versión 1.1 (rama `mejoras`), Mining Star usa **solo PostgreSQL**, en desarrollo, en las pruebas automáticas y en producción (Railway). SQLite ya no se usa.

## ¿Por qué un solo motor?

- **El mismo comportamiento en todos lados.** SQLite y PostgreSQL difieren en detalles (tipos de datos, mayúsculas en las búsquedas, restricciones, concurrencia). Si se desarrolla con uno y se publica con otro, aparecen errores que solo se ven en producción.
- **Varios usuarios a la vez.** PostgreSQL maneja muchas conexiones simultáneas; SQLite bloquea la base completa en cada escritura.
- **Las pruebas valen.** Las 119 pruebas del backend se ejecutan sobre PostgreSQL, el mismo motor de producción.
- **Más fácil de explicar.** Un solo motor, una sola configuración.

## Cómo se conecta Django

`config/settings.py` lee la variable `DATABASE_URL`:

| Ambiente | DATABASE_URL |
|---|---|
| Producción (Railway) | La crea Railway: `${{Postgres.DATABASE_URL}}` |
| Desarrollo local | Si no se define, se usa `postgres://miningstar:miningstar@localhost:5432/miningstar` |

## Instalar PostgreSQL en el equipo (elija una opción)

### Opción A — Docker (recomendada si ya tiene Docker Desktop)

En la carpeta del proyecto:

```
docker compose up -d
```

Eso crea la base `miningstar` con el usuario `miningstar` (clave `miningstar`), que es justo la que espera Django. Los datos se guardan en un volumen y sobreviven a `docker compose down`.

### Opción B — Instalador de PostgreSQL para Windows

1. Descargue PostgreSQL 16 desde https://www.postgresql.org/download/windows/ e instálelo (deje el puerto 5432). Anote la clave que le pide para el usuario `postgres`.
2. Abra **SQL Shell (psql)**, entre con el usuario `postgres` y ejecute:

```sql
CREATE USER miningstar WITH PASSWORD 'miningstar' CREATEDB;
CREATE DATABASE miningstar OWNER miningstar;
```

(`CREATEDB` es necesario para que `manage.py test` pueda crear la base temporal de las pruebas.)

## Dejar el sistema funcionando

```
pip install -r requirements.txt
python manage.py migrate
python manage.py cargar_demo --clave "<clave para los usuarios demo>"
python manage.py runserver
```

## Pasar los datos que ya tenía en SQLite (solo una vez)

Si en su equipo tenía datos propios en `db.sqlite3` y quiere conservarlos:

```
# 1. Exportar desde SQLite (se indica la base vieja solo para este comando)
set DATABASE_URL=sqlite:///db.sqlite3
python manage.py dumpdata --natural-foreign --natural-primary --exclude=contenttypes --exclude=auth.permission --exclude=sessions --exclude=token_blacklist --indent=2 -o datos_sqlite.json
set DATABASE_URL=

# 2. Cargar en PostgreSQL
python manage.py migrate
python manage.py loaddata datos_sqlite.json
```

En Linux o macOS se usa `export DATABASE_URL=...` en lugar de `set`.

## Respaldos

| Comando | Qué hace |
|---|---|
| `python manage.py respaldar_bd` | Crea `respaldos/mining_star_<fecha>.json` con todos los datos y, si `pg_dump` está instalado, también una copia `.dump` nativa de PostgreSQL. Conserva los 10 más recientes. |
| `python manage.py restaurar_bd respaldos/<archivo>.json` | Guarda primero el estado actual y luego reemplaza los datos por los del respaldo, dentro de una transacción (si falla, nada cambia). |
| `pg_restore --clean --dbname=miningstar respaldos/<archivo>.dump` | Restaura la copia nativa con las herramientas de PostgreSQL. |

En Railway, la carpeta `respaldos/` del servidor se borra en cada despliegue; allí conviene descargar los respaldos o usar las copias de la base de datos que ofrece la propia plataforma.
