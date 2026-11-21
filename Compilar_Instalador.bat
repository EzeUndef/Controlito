@echo off
title Compilador de Instalador - Controlito
echo ========================================================
echo       COMPILANDO INSTALADOR SETUP DE CONTROLITO
echo ========================================================
echo.

set ISCC_PATH="%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
if not exist %ISCC_PATH% (
    set ISCC_PATH="C:\Program Files\Inno Setup 6\ISCC.exe"
)
if not exist %ISCC_PATH% (
    set ISCC_PATH="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
)

if not exist %ISCC_PATH% (
    echo [ERROR] No se encontro Inno Setup 6.
    echo Por favor instala Inno Setup o ejecuta: winget install JRSoftware.InnoSetup
    pause
    exit /b 1
)

echo Compilando instalador con Inno Setup...
%ISCC_PATH% installer\controlito_setup.iss

if %ERRORLEVEL% equ 0 (
    echo.
    echo ========================================================
    echo  INSTALADOR GENERADO CON EXITO EN:
    echo  dist_installer\Controlito_Setup_v1.2.0.exe
    echo ========================================================
) else (
    echo.
    echo [ERROR] Fallo la compilacion del instalador.
)

pause
