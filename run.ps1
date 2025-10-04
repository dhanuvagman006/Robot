# Activates venv and runs the Flask app on 127.0.0.1:5050
param(
    [string]$Host = "127.0.0.1",
    [int]$Port = 5050
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path -Path "app/.venv/Scripts/Activate.ps1")) {
    Write-Host "Creating virtual environment..."
    python -m venv app/.venv
}

. "app/.venv/Scripts/Activate.ps1"

# Install deps if needed
pip show flask | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "Installing dependencies..."
    pip install -r requirements.txt
}

$env:HOST = $Host
$env:PORT = $Port

python -m app.app