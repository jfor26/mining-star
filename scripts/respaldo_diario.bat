@echo off
REM ==========================================================
REM Mining Star - copia de seguridad de la base de datos.
REM Programarla en Windows: Programador de tareas > Crear tarea basica >
REM Diariamente 11:00 p. m. > Iniciar un programa > este archivo.
REM ==========================================================
cd /d "%~dp0.."
call .venv\Scripts\activate.bat
if not exist respaldos mkdir respaldos
python manage.py respaldar_bd --conservar 15 >> respaldos\bitacora_respaldos.txt 2>&1
