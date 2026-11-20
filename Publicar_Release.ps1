# Script de PowerShell para publicar una nueva Release oficial en GitHub
param (
    [string]$Tag = "v1.2.0",
    [string]$Title = "Controlito v1.2.0 - Edición Empresarial",
    [string]$Notes = "Lanzamiento oficial de Controlito v1.2.0 con estética empresarial (Segoe UI), panel de configuración restaurado y gestión completa de finanzas personales."
)

$ErrorActionPreference = "Stop"
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  PUBLICADOR DE RELEASES DE CONTROLITO EN GITHUB" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$InstallerPath = Join-Path $PSScriptRoot "dist_installer\Controlito_Setup_v1.2.0.exe"
if (-not (Test-Path $InstallerPath)) {
    Write-Host "[ERROR] No se encontró el instalador en: $InstallerPath" -ForegroundColor Red
    Write-Host "Ejecuta primero: Compilar_Instalador.bat" -ForegroundColor Yellow
    exit 1
}

$InstallerSize = (Get-Item $InstallerPath).Length / 1MB
Write-Host "Instalador encontrado: Controlito_Setup_v1.2.0.exe ({0:N2} MB)" -f $InstallerSize -ForegroundColor Green

# Obtener token de GitHub desde Git Credential Manager
Write-Host "Obteniendo credenciales de GitHub..." -ForegroundColor Cyan
$gcmOutput = echo "protocol=https`nhost=github.com" | git credential fill
$tokenLine = $gcmOutput | Select-String "password="
if (-not $tokenLine) {
    Write-Host "[ERROR] No se pudo obtener el token de autenticación de GitHub." -ForegroundColor Red
    exit 1
}
$Token = $tokenLine.ToString().Replace("password=", "").Trim()

# Headers para GitHub API
$Headers = @{
    "Authorization" = "token $Token"
    "Accept"        = "application/vnd.github.v3+json"
    "User-Agent"    = "Controlito-Release-Publisher"
}

# 1. Crear la Release vía REST API
Write-Host "Creando Release $Tag en EzeUndef/Controlito..." -ForegroundColor Cyan
$ReleaseBody = @{
    tag_name         = $Tag
    target_commitish = "main"
    name             = $Title
    body             = $Notes
    draft            = $false
    prerelease       = $false
} | ConvertTo-Json

try {
    $Release = Invoke-RestMethod -Uri "https://api.github.com/repos/EzeUndef/Controlito/releases" -Method Post -Headers $Headers -Body $ReleaseBody
} catch {
    # Si la release ya existe, obtenerla
    Write-Host "La release ya existe o hubo aviso: $_" -ForegroundColor Yellow
    $Release = Invoke-RestMethod -Uri "https://api.github.com/repos/EzeUndef/Controlito/releases/tags/$Tag" -Headers $Headers
}

$ReleaseId = $Release.id
$UploadUrl = $Release.upload_url -replace '\{\?name,label\}', "?name=Controlito_Setup_v1.2.0.exe"
Write-Host "Release ID: $ReleaseId" -ForegroundColor Green

# 2. Subir el binario del instalador .exe como asset de la Release
Write-Host "Subiendo archivo instalador ($InstallerPath) a GitHub Releases..." -ForegroundColor Cyan
$UploadHeaders = @{
    "Authorization" = "token $Token"
    "Content-Type"  = "application/octet-stream"
    "User-Agent"    = "Controlito-Release-Publisher"
}

$UploadResult = Invoke-RestMethod -Uri $UploadUrl -Method Post -Headers $UploadHeaders -InFile $InstallerPath

Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  ¡RELEASE PUBLICADA CON ÉXITO EN GITHUB!" -ForegroundColor Green
Write-Host "  URL: https://github.com/EzeUndef/Controlito/releases/tag/$Tag" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Green
