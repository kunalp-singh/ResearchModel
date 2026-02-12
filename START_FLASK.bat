@echo off
title SecurNet Flask Server
color 0A

echo ====================================================================
echo   SecurNet Flask Server
echo ====================================================================
echo.

echo [1/3] Killing any existing Python processes...
taskkill /F /IM python.exe /T 2>nul
timeout /t 3 /nobreak >nul

echo.
echo [2/3] Changing to project directory...
cd /d "c:\Users\asus\Downloads\Epics\SecurNet---An-EPICS-Project-main"
echo     Current directory: %CD%

echo.
echo [3/3] Starting Flask server...
echo ====================================================================
echo.

set PYTHONUNBUFFERED=1
"C:\Users\asus\Downloads\Epics\.venv\Scripts\python.exe" flask_app.py

pause
