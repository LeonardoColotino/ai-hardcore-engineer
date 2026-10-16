# Independent delegated QA review

QA agent reviewed the challenge, final prompt, both feedback files, baseline supervisor/persistence/API/tests, and reference project's real-SQLite concurrency tests. No reference code was copied. Cases were independently authored and frozen in `evaluation/qa_validation_frozen.json` with a SHA-256 sidecar before candidate changes were tested. Cases used for fixes are now development regressions, not an unseen final holdout.

## Execution

- Initial interpreter lacked pytest; dependency installation succeeded. This is an installed runtime, not Docker.
- `python -m pytest -q` baseline: **92 passed**, 1 dependency warning, 5.77 s (`baseline.txt`). This is the attached base's applicable tests, not claimed historic 149.
- New QA round: 6 passed / 1 failed (`qa_before.txt`). Reproduced active ticket not blocking support and missing existing protocol in followup. Fixed in supervisor.
- Expanded QA round: **18 passed**, 1 warning (`qa_after.txt`).
- Full candidate round 1: 110 passed / 2 failed (`suite_qa_round1.txt`). Both were obsolete fixture/contract assumptions, retained and adapted below.
- Full candidate round 2: **112 passed**, 1 warning, 7.99 s (`suite_qa_round2.txt`). Later modifications require a final rerun by coordinator.

## New coverage

Production API and SQLite run for: mixed intentions both orders; preserving valid private support result when Knowledge fails; persistent single active ticket under 16 concurrent requests; operator resolution race producing exactly one human message; forced history-write rollback preserving IN_PROGRESS; ownership after Store reload; active handoff suppression and automation resumption; idempotent HTTP retry/conflict and four concurrent sends; trace and feedback ownership. Specialist calls/LLM are simulated. Web privacy cases assert service not called. Three forced task plans inject first/middle/last failure and verify other results survive. These prove engineering behavior, not live semantic quality.

## Preserved tests with contract updates

- `test_trace_context_reset_after_unhandled_tool_failure`: original reset assertion retained. Task-local exception is now contained by design; assert persistent escalation and failed task outcome rather than leaked RuntimeError.
- `test_html_div_content_survives`: original content/menu assertions retained. Network mock now models streamed HTTP chunks/status/headers and public DNS after ingestion hardening; no real internet used.
- No prior test was deleted. Historical second/third/fourth live regression files were not present in the uploaded base and are not falsely claimed restored.

## Limitations and gates

Engineering cases above: passed. Runtime Docker, Ollama inference, external web/current official corpus, browser E2E and factual semantic review: not established by this QA suite. Frozen question set contains explicit live/memory/source-injection scenarios needing broader validation; a dataset case is not a passing test by mere presence. Concurrency is one process with real SQLite threads, not distributed scale certification. Generic injection/PII immunity is not claimed. The installed FastAPI/Starlette initially differ from pinned requirements and produce a deprecation warning; coordinator must verify pinned install before release.
