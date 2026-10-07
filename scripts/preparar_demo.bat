@echo off
REM ==========================================================
REM Mining Star - instala dependencias y carga los datos de demostracion.
REM Uso: scripts\preparar_demo.bat "UnaClaveSegura2026*"
REM La clave queda para los 7 usuarios demo (gerente, admin.ms, supervisor,
REM comercial, contador, operario, auxiliar).
REM ==========================================================
if "%~1"=="" (
  echo Indique la clave de los usuarios demo. Ejemplo: scripts\preparar_demo.bat "Demo*Mina2026"
  exit /b 1
)
cd /d "%~dp0.."
call .venv\Scripts\activate.bat
pip install -r requirements-dev.txt
python manage.py migrate
python manage.py respaldar_bd
python manage.py cargar_demo --clave "%~1"
