$ErrorActionPreference = "Stop"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
. .\.venv\Scripts\Activate.ps1

Write-Host "Checking Ollama..."
ollama --version
if ($LASTEXITCODE -ne 0) { throw "Command failed; stopping script." }
ollama pull llama3.2:3b
if ($LASTEXITCODE -ne 0) { throw "Command failed; stopping script." }
ollama pull nomic-embed-text
if ($LASTEXITCODE -ne 0) { throw "Command failed; stopping script." }

$envPath = ".env"
if (-not (Test-Path $envPath)) { Copy-Item .env.example $envPath }
$content = Get-Content $envPath -Raw
$content = $content -replace 'LLM_PROVIDER=disabled', 'LLM_PROVIDER=ollama'
Set-Content $envPath $content -Encoding UTF8

Write-Host "Rebuilding RAG index with Ollama embeddings..."
python -m app.rag.ingest --ollama-embeddings
if ($LASTEXITCODE -ne 0) { throw "Command failed; stopping script." }
Write-Host "Ollama connection configured. Start the API with .\scripts\run_windows.ps1"
