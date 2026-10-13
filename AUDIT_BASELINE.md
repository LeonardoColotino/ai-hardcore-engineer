# Baseline audit

Observed UTC: 2026-10-12T19:08:57.957028+00:00. Source: immutable uploaded V3 ZIP. This audit is static; QA owns baseline execution evidence. Historical live JSON predates patches and is not candidate validation.

Direct code findings: supervisor persists real tickets while Escalation says no ticket; metadata says recommended/false; repeated escalation stages; specialist fallback loses metadata; conversational product list fabricated from word solutions; reference regex is finite; trace ContextVar reset missing finally; routing spends LLM calls before deterministic clear intents; payment tool matches isolated pagamento; RAG uses score without topic relevance; excerpts truncate at 220 characters; vector load lacks finite/dimension/provider checks; overlap starts inside words.

Existing strengths retained: authenticated API/owner checks, SQLite history and ticket state machine, operator assignment, direct specialist dataflow, NumPy cosine index, seed/offline evaluation, Docker non-root.

Risks: missing real Ollama/Docker/browser runtimes must remain pending; no local substitute can prove real model groundedness. Demo seed has official-looking URLs but is synthetic. Hash vectors and synthetic seeds must not become official evidence.
