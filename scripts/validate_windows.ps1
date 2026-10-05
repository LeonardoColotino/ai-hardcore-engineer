$ErrorActionPreference = "Stop"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
. .\.venv\Scripts\Activate.ps1

Write-Host "1/5 - Unit/integration/failure tests"
python -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Command failed; stopping script." }

Write-Host "2/5 - Offline AI evaluation"
python -m evaluation.run
if ($LASTEXITCODE -ne 0) { throw "Command failed; stopping script." }

Write-Host "3/5 - Live Getnet ingestion"
if ((Get-Content .env -Raw) -match '(?m)^LLM_PROVIDER=ollama\s*$') {
    python -m app.rag.ingest --ollama-embeddings
} else {
    python -m app.rag.ingest
}
if ($LASTEXITCODE -ne 0) { throw "Live ingestion failed." }

Write-Host "4/5 - Optional Ollama smoke check"
if ((Get-Content .env -Raw) -match 'LLM_PROVIDER=ollama') {
    ollama list
    if ($LASTEXITCODE -ne 0) { throw "Command failed; stopping script." }
    python -c "from app.services.llm import create_llm_client; from app.config import get_settings; print(create_llm_client(get_settings()).generate('Reply with OK only.','health check'))"
    if ($LASTEXITCODE -ne 0) { throw "Command failed; stopping script." }
} else {
    Write-Host "Ollama disabled in .env; skipping LLM smoke test."
}

Write-Host "5/5 - Docker validation"
if (Get-Command docker -ErrorAction SilentlyContinue) {
    docker compose config
    if ($LASTEXITCODE -ne 0) { throw "Command failed; stopping script." }
    docker compose build
    if ($LASTEXITCODE -ne 0) { throw "Command failed; stopping script." }
    Write-Host "Docker build completed. Run 'docker compose up' for an interactive smoke test."
} else {
    Write-Warning "Docker CLI not installed; Docker validation skipped."
}

Write-Host "Pre-submission validation completed. Review evaluation/report.json and README limitations before pushing."
