# Requirements Matrix

| Requirement | Type | Implementation | Validation | Status |
|---|---|---|---|---|
| Router Agent | Mandatory | Hybrid structured-LLM + deterministic fallback | unit/evaluation | Implemented |
| Knowledge Agent | Mandatory | RAG + web source selection | unit/integration | Implemented |
| Support Agent | Mandatory | account-scoped tools | unit/integration | Implemented |
| 2+ support tools | Mandatory | customer, transaction, payment | unit | Implemented |
| Agent communication | Mandatory | Orchestrator direct calls/data contracts | integration | Implemented |
| RAG | Mandatory | ingest/clean/chunk/metadata/embed/store/retrieve | unit + live ingest pending | Implemented |
| Getnet data source | Mandatory | configured official URLs | live ingest pending | Implemented |
| Web search | Mandatory | isolated DuckDuckGo adapter | mocked/unit + live pending | Implemented |
| POST API | Mandatory | FastAPI `/chat` | integration | Implemented |
| Docker | Mandatory | Dockerfile + Compose | target Docker validation pending | Implemented |
| Test strategy | Mandatory | unit/integration/failure separation | pytest | Implemented |
| README | Mandatory | setup, architecture, RAG, tools, tests, eval, tradeoffs | review | Implemented |
| 4th agent | Bonus | Human Escalation Agent | router/integration | Implemented |
| Guardrails | Bonus | secret/injection input checks | unit | Implemented |
| Human handoff | Bonus | explicit escalation flow | integration | Implemented |
| Evaluation/observability | Bonus | dataset/runner + structured logs | eval/tests | Implemented |
| GitHub repo | Deliverable | user pushes generated project | external action | Pending |
| Video | Deliverable | walkthrough outline included | external action | Pending |
