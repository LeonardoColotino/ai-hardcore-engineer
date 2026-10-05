$ErrorActionPreference = "Stop"
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass -Force
. .\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
if ($LASTEXITCODE -ne 0) { throw "Command failed; stopping script." }
