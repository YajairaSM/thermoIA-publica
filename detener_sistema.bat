@echo off
title Detener ThermoIA
color 0C

echo.
echo  Deteniendo ThermoIA...
echo.

:: Matar procesos de streamlit en puertos 8501 y 8502
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8501"') do taskkill /F /PID %%a 2>nul
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8502"') do taskkill /F /PID %%a 2>nul

echo  Apps detenidas correctamente.
echo.
pause
