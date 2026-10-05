# Final review

See `VALIDATION_REPORT.md` for the current executed checks.

The uploaded project is an offline-capable prototype with four Python agent components.
Support uses synthetic JSON records through real local lookup tools; these are not Getnet APIs.
The backend is NumPy exact cosine search, not FAISS. Offline hashing embeddings are lexical,
not a multilingual semantic model. The Router fallback relies on regex and cannot cover every paraphrase.
The model-produced confidence is not calibrated. The human handoff only recommends review;
it has no operator queue or ticket integration. `user_id` filtering is not authentication or authorization.
Input pattern guardrails are limited and do not guarantee protection from arbitrary prompt injection.
Web snippets can be stale or incomplete; generated factual quality remains unmeasured.

These limitations must be explained in the submission. Validate the live dependencies before
claiming RAG from actual websites, LLM quality or reproducible Docker operation.
Do not present deterministic 100% results as general system quality.
