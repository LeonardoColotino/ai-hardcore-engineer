$ErrorActionPreference = "Stop"
Set-Location (Split-Path $PSScriptRoot -Parent)
& .\.venv\Scripts\python.exe -m pytest -q
if ($LASTEXITCODE -ne 0) { throw "Testes falharam" }
& .\.venv\Scripts\python.exe -m evaluation.run
if ($LASTEXITCODE -ne 0) { throw "Avaliação offline falhou" }
