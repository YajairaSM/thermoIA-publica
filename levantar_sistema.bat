@echo off
title ThermoIA - Sistema de Alertas de Calor
color 0A

echo.
echo  ============================================
echo   ThermoIA - Sistema de Alertas de Calor
echo   David, Chiriqui, Panama
echo  ============================================
echo.

:: Activar entorno conda
call conda activate prediccion_ia

:: Ir a la raiz del proyecto
cd /d C:\Users\Yajaira\Desktop\PROYECTO_PREDICCION_IA

echo  Levantando App Publica   (puerto 8502)...
start "ThermoIA - Publica" cmd /k "conda activate prediccion_ia && streamlit run app/app_publica.py --server.port 8502 --server.headless false"

:: Esperar 3 segundos
timeout /t 3 /nobreak > nul

echo  Levantando App Admin     (puerto 8501)...
start "ThermoIA - Admin" cmd /k "conda activate prediccion_ia && streamlit run app/app.py --server.port 8501 --server.headless false"

:: Esperar 4 segundos para que arranquen
timeout /t 4 /nobreak > nul

echo.
echo  Abriendo navegador...
start http://localhost:8502
timeout /t 2 /nobreak > nul
start http://localhost:8501

echo.
echo  ============================================
echo   Apps corriendo:
echo   Publica : http://localhost:8502
echo   Admin   : http://localhost:8501
echo  ============================================
echo.
echo  Para detener: cierra las ventanas negras
echo  de ThermoIA-Publica y ThermoIA-Admin
echo.
pause
