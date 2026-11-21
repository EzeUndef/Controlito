@echo off
echo ========================================================
echo        Compilando Controlito a Ejecutable Windows (.exe)
echo ========================================================
echo.

rem Asegurar que customtkinter y matplotlib se incluyan con todos sus assets
python -m PyInstaller --noconfirm --onedir --windowed ^
    --icon "assets/icon.ico" ^
    --add-data "assets;assets" ^
    --collect-all customtkinter ^
    --collect-all matplotlib ^
    --name "Controlito" ^
    main.py

echo.
if exist "dist\Controlito\Controlito.exe" (
    echo [EXITO] Controlito.exe ha sido generado en: dist\Controlito\Controlito.exe
) else (
    echo [ERROR] Hubo un problema durante la compilacion.
)
pause
