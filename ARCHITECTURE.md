# Architecture and trust boundaries

FastAPI bearer identity → Supervisor owner check and bounded session lock → input guardrail → persisted conversation state/reference resolution → Router policy first, structured LLM only when ambiguous → specialist(s) → evidence/outcome normalization → SQLite ticket if unresolved → assistant/history and JSON tracing.

SQLite stores sessions, user/assistant/human messages, conversation state and tickets. Identity enters only from authentication, never model/document text. Support tools receive authenticated subject. Operators follow OPEN → IN_PROGRESS → RESOLVED (human reply persisted) → CLOSED with assignment checks.

Knowledge: official ingestion → structure-preserving cleanup/chunks → provider-compatible NumPy embeddings/index → cosine retrieval plus topic filtering → bounded context generation → explicit provenance/limited safeguards → answer or abstention. Seed is separate synthetic demo; similarity and lexical checks never guarantee factual grounding. General questions use web; Getnet fallback only accepts official domains. Sources are untrusted data.

Collaboration: Support verifies account and produces diagnostic; Knowledge consumes actual diagnostic to retrieve relevant guidance. No evidence means real ticket, never false resolution. Maximum two specialist stages and one handoff; no recursive replanning.

Tradeoffs: SQLite and direct functions fit demonstration; per-process locks/rate metrics are not distributed; production requires shared rate limiting, stronger auth, durable observability and evidence verifier. Ollama is replaceable through LLMClient protocol.
