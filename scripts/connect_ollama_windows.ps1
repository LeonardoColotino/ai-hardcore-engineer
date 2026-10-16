$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
ollama show llama3.2:3b *> $null
if ($LASTEXITCODE -ne 0) { throw "Modelo llama3.2:3b ausente; instale-o explicitamente com ollama pull llama3.2:3b" }
if ($LASTEXITCODE -ne 0) { throw "Ollama indisponível" }
ollama show nomic-embed-text:latest *> $null
if ($LASTEXITCODE -ne 0) { throw "Modelo nomic-embed-text:latest ausente; instale-o explicitamente com ollama pull nomic-embed-text:latest" }
if ($LASTEXITCODE -ne 0) { throw "Modelo de embeddings indisponível" }
$env:LLM_PROVIDER = "ollama"
& .\.venv\Scripts\python.exe -m app.rag.ingest --ollama-embeddings
if ($LASTEXITCODE -ne 0) { throw "Ingestão real falhou; não use seed como evidência real" }
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
