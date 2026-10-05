# Pre-submission procedure (Windows)

Run these steps on the machine that will be used for the final GitHub submission.

## 1. Setup

```powershell
.\scripts\setup_windows.ps1
```

## 2. Connect Ollama

Only when Ollama is installed and running:

```powershell
.\scripts\connect_ollama_windows.ps1
```

The script pulls `llama3.2:3b` and `nomic-embed-text`, enables `LLM_PROVIDER=ollama`, and rebuilds the RAG index using Ollama embeddings.

## 3. Validate everything

```powershell
.\scripts\validate_windows.ps1
```

Do **not** claim the Ollama, live ingestion, or Docker paths were validated until this succeeds on your machine.

## 4. Manual API smoke

```powershell
.\scripts\run_windows.ps1
```

Open `http://127.0.0.1:8000/docs` and execute at least:

- Getnet product/RAG question;
- general/current Web Search question;
- customer settlement question;
- transaction decline question;
- unknown customer/fallback;
- guardrail case.

## 5. Git check

Before push:

```powershell
git status
git diff --check
git ls-files | Select-String -Pattern "\.env$|vector_store|__pycache__"
```

Confirm `.env`, local vector indexes, caches, credentials and logs are not committed.

## 6. Video

Use the 10-step outline at the end of `README.md`. Show evidence instead of only describing the code: Swagger, tests, evaluation report, logs, RAG sources and one fallback.
