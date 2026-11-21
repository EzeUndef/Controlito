# Script de PowerShell para publicar una nueva Release oficial en GitHub
Write-Host "Iniciando publicador oficial de Releases para Controlito..." -ForegroundColor Cyan

$python = (Get-Command python -ErrorAction SilentlyContinue).Source
if (-not $python -or $python -like "*WindowsApps*") {
    $candidates = @(
        "$env:LOCALAPPDATA\Programs\Python\Python312\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python311\python.exe",
        "$env:LOCALAPPDATA\Programs\Python\Python310\python.exe",
        "C:\Python312\python.exe",
        "C:\Python311\python.exe",
        "C:\Python310\python.exe",
        "C:\Python315\python.exe"
    )
    foreach ($cand in $candidates) {
        if (Test-Path $cand) {
            $python = $cand
            break
        }
    }
}

if (-not $python) {
    Write-Host "[ERROR] No se encontró Python instalado en el sistema." -ForegroundColor Red
    exit 1
}

& $python "$PSScriptRoot\utils\publish_release.py"
