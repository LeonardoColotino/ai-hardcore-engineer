> Reviewed on 2026-10-05: 46 tests passed; 17 offline evaluation cases passed.
> Start with `COMECE_AQUI.md` for Windows setup and corrected limitations.
> Offline seeds and customer JSON are synthetic demos. The API does not authenticate users,
> and human handoff recommends review without creating a ticket. The vector backend is NumPy.
> Excerpt presence does not prove factual grounding. Ollama, live websites, Docker and PowerShell
> execution have not been validated in this review environment.

# AI Hardcore Engineer — Multi-Agent Support System v2

Second-attempt implementation of the AI Hardcore Engineer challenge. The project is intentionally **local-first**, testable without paid APIs, and structured so Ollama can be connected later without changing the agent architecture.

## Problem

Build an HTTP service in which multiple AI agents cooperate to route requests, retrieve Getnet knowledge, use web search for general/current questions, and resolve customer-support requests with account-scoped tools.

## Architecture

```text
User -> FastAPI /chat -> Guardrails -> Router/Orchestrator
                                      |-> Knowledge Agent -> RAG -> Vector Store
                                      |                   -> Web Search
                                      |-> Support Agent   -> Customer Lookup
                                      |                   -> Transaction Lookup
                                      |                   -> Payment Status
                                      |-> Escalation Agent -> Human handoff

Cross-cutting: LLM service | structured JSON logs | evaluation | error handling
```

### Why this architecture

- **Real separation of responsibilities:** agents decide; tools execute operations; services encapsulate external I/O.
- **Offline-first:** deterministic routing, local hashing embeddings and mock customer data let tests run without Ollama or internet.
- **Provider isolation:** Ollama is hidden behind `LLMClient`/embedding services.
- **Safe fallback:** low-confidence or unsupported cases go to escalation instead of hallucinating.
- **Reproducibility:** tests mock external dependencies and the RAG index can be built either from live sources or a tiny explicit seed corpus.

## Agents

### Router Agent
Produces a validated `RoutingDecision` with `agent`, `reason`, `confidence`, and `source`. When Ollama is enabled it attempts structured LLM classification first; invalid/low-confidence output falls back to deterministic keyword/regex rules.

### Knowledge Agent
Uses RAG for Getnet/product knowledge and web search for time-sensitive/general questions. It refuses to fabricate evidence and escalates when both sources fail.

### Customer Support Agent
Uses account-scoped tools. A request can never query another user's records because every repository query filters on the request `user_id`.

### Human Escalation Agent
Handles low-confidence routing, unknown customers, unavailable evidence and unresolved support cases.

## Tools

- `rag_search`
- `web_search`
- `customer_lookup`
- `transaction_lookup`
- `payment_status`
- `human_handoff` (orchestration action)

Tools return a predictable `ToolResult` structure with success, data, errors, sources and metadata.

## RAG pipeline

```text
Getnet URLs
 -> HTTP fetch
 -> HTML cleanup
 -> text normalization
 -> overlapping chunks
 -> metadata (title/url/source/document_id/chunk_id)
 -> embeddings
 -> persistent NumPy cosine vector store
 -> top-k retrieval
 -> similarity threshold
 -> deduplication
 -> grounded generation / excerpt fallback
```

A NumPy vector store is used to keep the challenge runtime small and transparent. Its interface is isolated so FAISS/Qdrant can replace it without changing agents.

### Current configured Getnet sources

- `https://www.getnet.net/en`
- `https://www.getnet.net/en/our-solutions/online-payments`
- `https://site.getnet.com.br/pix/`
- `https://site.getnet.com.br/link-de-pagamento/`
- `https://site.getnet.com.br/conta-digital/`

Override with `RAG_SOURCE_URLS` (semicolon-separated).

## Routing strategy

1. If Ollama is enabled, request a strict JSON routing decision.
2. Validate it with Pydantic.
3. Accept only decisions above `ROUTER_MIN_CONFIDENCE`.
4. On failure, use deterministic multi-pattern intent scoring.
5. Ambiguous cases go to Human Escalation.

This avoids relying exclusively on `if "word" in message` while remaining testable and available when the LLM is down.

## Technologies

Python, FastAPI, Pydantic, Requests, BeautifulSoup, NumPy, pytest, optional Ollama.

## Project structure

```text
app/
  agents/            router, knowledge, support, escalation
  api/               HTTP routes
  guardrails/        input checks
  models/            request/response/tool/routing contracts
  observability/     structured JSON logging
  orchestration/     workflow coordinator
  rag/               ingest, chunking, vector store, retrieval
  services/          LLM, embeddings, search, customer data
  tools/             independent tool adapters
  data/              demo customer/support records + generated index
evaluation/          dataset + deterministic runner
tests/               unit, integration, failure tests
```

## Setup

### Windows PowerShell

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

### Linux/macOS

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
cp .env.example .env
```

> `.env` is ignored by Git. Never commit real credentials.

## Run before Ollama is connected

Build a tiny explicit offline demo index:

```bash
python -m app.rag.ingest --seed
python -m uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Live Getnet ingestion

Internet is required:

```bash
python -m app.rag.ingest
```

The vector store is generated under `app/data/vector_store/` and intentionally ignored by Git.

## Connect Ollama later

1. Install Ollama.
2. Pull the models:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

3. In `.env`:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3.2:3b
OLLAMA_EMBED_MODEL=nomic-embed-text
```

4. Rebuild the index with Ollama embeddings:

```bash
python -m app.rag.ingest --ollama-embeddings
```

5. Run the API:

```bash
python -m uvicorn app.main:app --reload
```

**Important:** use the same embedding provider to build and query an index. The supplied code records the intended provider when the index is created.

## API

### `GET /health`

Returns service state, LLM provider, and whether the RAG index is ready.

### `POST /chat`

```json
{
  "message": "When will the money from my sales be deposited?",
  "user_id": "cliente1988"
}
```

Example response shape:

```json
{
  "request_id": "req-...",
  "agent": "support",
  "answer": "Latest settlement status: scheduled...",
  "tool": "payment_status",
  "sources": [],
  "escalated": false,
  "metadata": {
    "routing_confidence": 0.81
  }
}
```

## Tests

The default suite does **not** depend on Ollama or the internet.

```bash
python -m pytest -q
```

Coverage includes:

- router decisions and fallback;
- support tools and user isolation;
- chunking and retrieval;
- guardrails;
- API validation and integration;
- missing customer/data/index failure behavior.

External end-to-end tests should be run separately after Ollama and internet access are available.

## Evaluation

```bash
python -m evaluation.run
```

The offline dataset includes examples from the challenge and measures deterministic routing accuracy and tool-selection accuracy. It generates `evaluation/report.json`.

After live ingestion/Ollama connection, extend evaluation with:

- retrieval hit rate / Recall@K;
- minimum similarity score analysis;
- source excerpt presence checks (not factual grounding);
- abstention/fallback accuracy;
- latency percentiles.

Do not use an LLM-as-judge as the only quality metric.

## Current validation evidence

Validated in the generation environment with Ollama disabled:

- `46 passed` with `python -m pytest -q`.
- 17-case offline end-to-end evaluation: routing, tool selection, retrieval-source presence, source excerpt presence, and failure behavior all reached 100% after the final correction cycle.
- FastAPI was started with Uvicorn and `/health` plus representative `/chat` requests returned HTTP 200.
- Python import/compile checks passed.
- Live Getnet ingestion could **not** be validated in the generation container because outbound DNS resolution was unavailable.
- Docker could **not** be executed because the Docker CLI is not installed in the generation environment.
- Ollama validation is intentionally pending because it will be connected later on the target machine.

These limitations are recorded so the repository does not claim tests that were not actually executed.

## Observability

Requests emit structured JSON logs containing fields such as:

- `request_id`
- chosen `agent`
- `tool`
- `duration_ms`
- success/escalation status
- routing confidence
- retrieval metadata when available

Secrets and credentials are deliberately excluded from structured log metadata.

## Guardrails

The lightweight guardrail layer currently blocks:

- obvious secret/password/token submissions;
- common prompt-injection attempts requesting system instructions.

A production version should add policy enforcement, PII classification, rate limits and audit controls.

## Docker

```bash
docker build -t ai-hardcore-engineer-v2 .
docker run --rm -p 8000:8000 ai-hardcore-engineer-v2
```

or:

```bash
docker compose up --build
```

If Ollama runs on the host, Docker Compose defaults to `http://host.docker.internal:11434`.

## Design decisions and trade-offs

### No LangChain dependency
The challenge allows suitable libraries but does not require one. Here, explicit Python components make routing, failure behavior, tests and data flow easier to explain in an interview. LangGraph could be added if workflows become stateful or much more complex.

### NumPy vector store instead of FAISS
The corpus for the challenge is small, so exact cosine search is adequate and more reproducible across Python environments. At larger scale, FAISS/Qdrant/Pinecone would be appropriate.

### Deterministic fallback router
LLM-only routing creates an availability and testing dependency. The hybrid strategy preserves intelligent structured routing when Ollama exists and safe behavior when it does not.

### Mock customer data
The challenge does not provide a real customer backend. JSON records are clearly synthetic and exist only to demonstrate secure, account-scoped tools. In production they would be replaced by authenticated backend adapters.

## Known limitations

- Web search uses DuckDuckGo HTML and may change/break; production should use a supported search API.
- Offline hashing embeddings are development-oriented, not a replacement for production semantic embeddings.
- Guardrails are intentionally lightweight.
- No authentication layer is implemented because the challenge only provides `user_id`; production must authenticate identity before trusting it.
- Docker/Ollama live behavior must be validated in the target machine once Ollama is installed.

## Future improvements

- AuthN/AuthZ and tenant isolation.
- FAISS/Qdrant vector backend for larger corpora.
- OpenTelemetry traces and metrics dashboard.
- Prompt/version registry and richer regression datasets.
- Circuit breakers, retries with jitter, search-provider redundancy.
- Human-support ticket connector instead of simulated handoff.

## Submission checklist

- [x] 3 required agents
- [x] 4th Human Escalation Agent
- [x] RAG pipeline
- [x] Web Search tool
- [x] 2+ Support tools
- [x] FastAPI `/chat`
- [x] `/health`
- [x] Guardrails
- [x] Human handoff
- [x] Structured logging
- [x] Unit/integration/failure tests
- [x] Evaluation dataset/runner
- [x] Dockerfile / Compose
- [x] `.env.example`
- [x] README with decisions/trade-offs
- [ ] Live Ollama validation (after local connection)
- [ ] Live Docker validation on submission machine
- [ ] Video recording

## Video walkthrough outline

1. State the problem and mandatory requirements.
2. Show the architecture diagram.
3. Explain why Router/Knowledge/Support/Escalation are distinct.
4. Demonstrate `/health` and `/chat` in Swagger.
5. Run one RAG request, one support request, one web-search request and one escalation case.
6. Show the RAG metadata and source URLs.
7. Run `pytest` and `python -m evaluation.run`.
8. Show structured logs.
9. Explain Docker and Ollama provider isolation.
10. Close with trade-offs, limitations and production improvements.
