$ErrorActionPreference = "Stop"

if (-not (Test-Path ".venv")) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw "Command failed; stopping script." }
}

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
. .\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
if ($LASTEXITCODE -ne 0) { throw "Command failed; stopping script." }
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw "Command failed; stopping script." }

if (-not (Test-Path ".env")) {
    Copy-Item .env.example .env
    Write-Host "Created .env from .env.example (Ollama remains disabled)."
}

if (-not (Test-Path "app/data/vector_store/embedding_provider.txt")) {
    python -m app.rag.ingest --seed
    if ($LASTEXITCODE -ne 0) { throw "Seed ingestion failed." }
}
Write-Host "Setup completed. Run .\scripts\run_windows.ps1"
