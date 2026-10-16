$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
python -c "import sys; assert sys.version_info[:2] == (3, 12), 'Use Python 3.12'"
if ($LASTEXITCODE -ne 0) { throw "Python 3.12 requerido no PATH" }
python -m venv .venv
if ($LASTEXITCODE -ne 0) { throw "Python 3.12 requerido" }
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Instalação falhou" }
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
Write-Host "Configure AUTH_SECRET e DEMO_PASSWORD em .env. Depois execute run_windows.ps1."
