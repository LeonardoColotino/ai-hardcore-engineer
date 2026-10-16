# Candidate specification (fixed before implementation)

Challenge remains authoritative: three agents, Knowledge RAG + web, Support >=2 tools, HTTP, Docker, tests, README, repository/video preparation. No paid provider or public deployment.

## REQ-MEM-001
Objective/justification: Persist scoped conversation state, selected entities and actual presented candidates.
Acceptance: API restart and paraphrase preserve entity; ambiguity lists actual candidates; topic switch does not invent state.
Positive: Single entity continuation after restart. Negative: Foreign session and multiple candidates.
Owner: Implementation/QA. State: specified, pending validation.

## REQ-ROUTE-001
Objective/justification: Policy before LLM for explicit human, product, account and general intents.
Acceptance: No account tool for product/signup; human goes directly escalation.
Positive: Product signup and settlement routes. Negative: Misleading confident model route.
Owner: Implementation/QA. State: specified, pending validation.

## REQ-GROUND-001
Objective/justification: Filter topic/evidence and disclose generation provenance.
Acceptance: No irrelevant connectivity/other-product source; signup distinct from usage; seed labeled.
Positive: Relevant product evidence answered. Negative: High-vector irrelevant evidence abstains.
Owner: Implementation/QA. State: specified, pending validation.

## REQ-HITL-001
Objective/justification: Real persistent handoff with coherent states.
Acceptance: Ticket metadata/text matches SQLite OPEN record; stages accurate.
Positive: Operator lifecycle returns human reply. Negative: Unauthorized lifecycle rejected.
Owner: Implementation/QA. State: specified, pending validation.

## REQ-ENC-001
Objective/justification: Explicit UTF-8 across textual artifacts.
Acceptance: Portuguese survives read/write on Windows.
Positive: Accented text round trip. Negative: BOM/corrupt input diagnosed.
Owner: Implementation/QA. State: specified, pending validation.

## REQ-PERF-001
Objective/justification: Bound calls/context/output and observe outcomes.
Acceptance: At most router + one generation; clear intents zero router calls; timings and errors explicit.
Positive: Clear intent avoids router generation. Negative: Failure resets request tracing.
Owner: Implementation/QA. State: specified, pending validation.

## REQ-UI-001
Objective/justification: Integrated accessible chat and operator.
Acceptance: Responsive workflow, safe sources, ticket/history and errors.
Positive: Chat and operator end-to-end. Negative: Escaped malicious answer/link.
Owner: UI/QA. State: specified, pending validation.

## REQ-INFRA-001
Objective/justification: Reproducible Windows/Docker and honest readiness.
Acceptance: Missing/corrupt index is unready; liveness independent; persistent state.
Positive: Build/run/restart where available. Negative: Missing provider/index.
Owner: Implementation/QA. State: specified, pending validation.

Contract: bearer identity owns sessions; optional user_id must match identity. Missing session_id creates new session. Metadata includes generation_kind, resolved/outcome, persisted handoff status, ordered specialist stages, request/session IDs. Conversation state stores product selection, presented candidates, intent, last ticket and stage; context bounded to 12 recent messages. Human reply is role human. Demo seed is labeled and never counted as official grounding.

Performance acceptance REQ-PERF-001: warm serial representative chat p95 <=60 seconds, configurable total request budget (CHAT_BUDGET_S default 60), per-tool/generation/persistence stages. Real hardware latency remains pending until measured; call counts do not substitute this target. Lexical topic, signup and abstention gates are partial safeguards, never factual grounding guarantees.
