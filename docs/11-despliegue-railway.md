# Despliegue de Mining Star en Railway

Mining Star se publica en Railway como **dos servicios** creados desde este mismo repositorio, más una base de datos PostgreSQL administrada.

| Servicio | Carpeta raíz | Arranque | Variables clave |
|---|---|---|---|
| API (Django + DRF) | `/` | `bash scripts/iniciar_railway.sh` (migrate, collectstatic, gunicorn) | `DJANGO_SECRET_KEY`, `DJANGO_DEBUG=False`, `DJANGO_ALLOWED_HOSTS`, `DJANGO_CSRF_TRUSTED_ORIGINS`, `DJANGO_CORS_ORIGINS`, `DATABASE_URL`, `DEMO_CLAVE` (opcional) |
| Web (React + Vite) | `frontend` | `npm run build` y `npm run start` (serve) | `VITE_API_URL=https://<dominio-api>/api/v1` |
| PostgreSQL | — | Plantilla de Railway | Expone `DATABASE_URL` |

## Pasos
1. En Railway, **New Project → Deploy from GitHub repo** y elegir `mining-star`.
2. Agregar **PostgreSQL** al proyecto y referenciar `DATABASE_URL` en el servicio API (`${{Postgres.DATABASE_URL}}`).
3. Configurar las variables del servicio API y generar su dominio (**Settings → Networking → Generate Domain**).
4. Crear el segundo servicio desde el mismo repositorio con **Root Directory = `frontend`**, definir `VITE_API_URL` y generar su dominio.
5. Volver al servicio API y poner el dominio del frontend en `DJANGO_CORS_ORIGINS`.
6. Verificar: `https://<dominio-api>/api/docs/` responde 200 y el inicio de sesión funciona desde el dominio web.

Los archivos `railway.json` (raíz) y `frontend/railway.json` fijan el constructor (Railpack) y los comandos de arranque. Los archivos estáticos los sirve WhiteNoise y la sesión usa JWT en cabecera, por lo que no se requieren cookies entre dominios.
