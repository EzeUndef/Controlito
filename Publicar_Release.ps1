# Script de PowerShell para publicar una nueva Release oficial en GitHub
Write-Host "Iniciando publicador oficial de Releases para Controlito..." -ForegroundColor Cyan
& "C:\Python315\python.exe" utils\publish_release.py
