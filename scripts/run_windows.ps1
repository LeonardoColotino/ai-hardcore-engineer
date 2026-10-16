$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path app/data/demo_users.json)) {
  & .\.venv\Scripts\python.exe scripts/init_demo.py
  if ($LASTEXITCODE -ne 0) { throw "Configure as credenciais em .env" }
}
& .\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
