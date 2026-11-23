#!/usr/bin/env bash
# Arranque del back-end de Mining Star en Railway.
# 1) aplica migraciones, 2) recopila estaticos, 3) carga datos de
# demostracion si se definio DEMO_CLAVE (es idempotente) y 4) inicia Gunicorn.
set -e
python manage.py migrate --noinput
python manage.py collectstatic --noinput
if [ -n "$DEMO_CLAVE" ]; then
  python manage.py cargar_demo --clave "$DEMO_CLAVE"
fi
exec gunicorn config.wsgi --bind "0.0.0.0:${PORT:-8000}" --workers 2 --access-logfile -
