@echo off
REM ==========================================================
REM Mining Star - levanta la API Django en http://127.0.0.1:8000
REM Uso: doble clic, o desde la terminal de VS Code: scripts\iniciar_backend.bat
REM ==========================================================
cd /d "%~dp0.."
call .venv\Scripts\activate.bat
python manage.py migrate
python manage.py runserver 127.0.0.1:8000
