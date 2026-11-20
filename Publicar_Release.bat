@echo off
title Publicar Release en GitHub - Controlito
echo ========================================================
echo       PUBLICANDO RELEASE EN GITHUB RELEASES
echo ========================================================
echo.
powershell -ExecutionPolicy Bypass -File "%~dp0Publicar_Release.ps1"
echo.
pause
