# Validation report — 2026-10-05

## Executed on the reviewed project

- Python 3.12; `python -m pytest -q`: **46 passed**, 1 dependency deprecation warning.
- `python -m evaluation.run`: 17 deterministic offline scenarios; routing, tool selection,
  source presence, source excerpt presence and escalation behavior each scored 1.0.
- Started Uvicorn and sent HTTP requests: `/health` 200; support/payment, knowledge/RAG,
  unknown customer/escalation and absent evidence/escalation behaved as expected.
- HTTP evidence: `evaluation/http_smoke_report.json`. Offline metrics: `evaluation/report.json`.

The web evaluation uses a stub and the RAG corpus is synthetic. Excerpt presence only checks
whether an answer repeats part of a retrieved snippet; it does not measure factual correctness,
retrieval relevance, semantic grounding, current information or live LLM behavior.
Routing confidence is a heuristic or an LLM self-report, not a calibrated probability.

## Corrections

- Preserve originating agent/tool and stable handoff reason in response and JSON logs.
- Log `resolved` separately from successful request processing.
- Catch unavailable embeddings and corrupt/missing index files at the RAG tool boundary.
- Avoid duplicate web search and refuse snippetless evidence as a resolved answer.
- Validate request length after trimming whitespace.
- Improve Portuguese support/Pix intent detection.
- Force offline evaluation to use disabled LLM despite local `.env` settings.
- Keep the embedding provider of the existing index when chat generation is disabled.
- Windows validation preserves Ollama embeddings, checks native exit codes and stops on failure.
- Read Windows UTF-8 BOM `.env` files correctly.
- Use a separate Docker Ollama URL variable to avoid inheriting localhost from the host `.env`.
- Clarify demo handoff, demo data and absence of authentication.

## Not executed here

Ollama generation/embeddings, live Getnet ingestion, live DuckDuckGo, Docker build/runtime,
PowerShell scripts on Windows. Docker, Ollama and PowerShell executables are absent here.
No production readiness claim is made. No real support ticket or message is sent.
The original challenge documents were not included in this ZIP; full compliance with their
exact wording cannot be independently certified from the pasted summary alone.
