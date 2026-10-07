@echo off
REM ==========================================================
REM Mining Star - levanta el front-end React en http://localhost:5173
REM Requiere Node.js 20 o superior. La primera vez ejecuta "npm install".
REM ==========================================================
cd /d "%~dp0..\frontend"
if not exist node_modules call npm install
call npm run dev
