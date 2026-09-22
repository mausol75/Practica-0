# run.ps1 — Script para iniciar la aplicación Flask.
# Uso: powershell -ExecutionPolicy Bypass -File run.ps1

$ErrorActionPreference = "Stop"

$backendDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Activar el entorno virtual si existe
$venvActivate = Join-Path $backendDir "..\..\..\.venv\Scripts\Activate.ps1"
if (Test-Path $venvActivate) {
    & $venvActivate
}

# Iniciar la aplicación
Set-Location $backendDir
python app.py
