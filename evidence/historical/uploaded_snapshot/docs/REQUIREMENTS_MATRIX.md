# Matriz final de requisitos e evidência

D = desafio; F = feedback V2; P = master. Estado refere-se à evidência desta versão, não nota oficial. Revisão independente de IA: INDEPENDENT_REVIEW.md. Suíte final QA e validador:77 passam no Linux disponível; versões/hash em manifests. As mesmas 77 execuções não viram 154 testes distintos.

| ID / fonte | Código ou entrega | Teste / execução / evidência | Limitação e estado |
|---|---|---|---|
| REQ-ORCH-001 D/F/P | agents/router,knowledge,support,escalation; supervisor/orchestrator | test_real_dataflow; suíte77; stages revisados no probe | Colaboração limitada sequencial; implementado/testado determinístico, qualidade real pendente |
| REQ-API-001 D | FastAPI POST /chat; Pydantic; auth bearer | tests/integration/test_api.py; independent-probe.json | user_id opcional deve corresponder ao autenticado; implementado/testado |
| REQ-TOOLS-001 D/P | customer_lookup,transaction_lookup,payment_status | tests/unit/test_tools.py; suíte77 | Dados fictícios; integrações financeiras reais fora do escopo; implementado/testado |
| REQ-ROUTE-001 F/P | intents.py/router.py/support.py | test_clear_policy_overrides_misleading_llm; offline17 | Zero tool de conta indevida nas regressões; ≥95% final live pendente |
| REQ-MEM-001 F/P | Store.state/save_state; supervisor; sessões | test_memory_paraphrase_after_intermediate_message, corrected_entity_survives_persistence_reload, new_conversation_does_not_inherit_product; tests V3 restart/isolation | Estado persistido reconhece catálogo lexical; memória semântica geral e repetições live pendentes; parcial |
| REQ-SEC-001 F/P | security.py; customer/identity; Store.check | Token/conta/papel tests V3; independent probe404/403 | Demo HMAC/PBKDF2; sem revogação por dispositivo; demonstrativo testado |
| REQ-HITL-001 D bônus/F/P | tickets persistentes, transition transacional, UI operador | handoff_cycle_and_authorization; persisted_handoff_metadata_truth; independent SQLite CLOSED+human reply | Sem mensagens externas e idempotência completa; ciclo backend testado; browser pendente |
| REQ-GROUND-001 P | relevance.py; Knowledge; outcome/generation_kind | high_score_wrong_product_not_resolution, disclaimer_or_cta_is_not_contracting_procedure; probe disclaimer False | Heurísticas não verificam cada claim; útil≥90%, qualidade≥1,8/2 e critical claims live pendentes; parcial |
| REQ-RAG-001 D/P | ingest/chunking/store/retriever; manifeste e metadata novos | tests/unit/test_rag.py, chunking.py; failure cases; revisão dos20 chunks históricos | Corpus anexado legado sem manifesto/date/modelo; reconstrução oficial e avaliação relevância pendentes; parcial |
| REQ-ENC-001 P | UTF-8 explícito produção/runners/fixtures novos | suíte; artifacts tests; JSON probe mantém acentos | Windows não executado; Linux testado, Windows pendente |
| REQ-LLM-001 D/P | serviços provider/embeddings; fallback classificado | test_llm_transport.py/regressions;77 | Mocks não confirmam Ollama/modelo real; pendente integração |
| REQ-PERF-001 P | budget.py; generation limites; métricas p50/p95 | Clear policy sem router LLM; trace_context_reset_after_unhandled_tool_failure; suíte | Deadline entre etapas/socket não cancelamento duro; p95warm≤60s não medido; parcial |
| REQ-GUARD-001 D bônus/P | guardrails; prompt untrusted; redação; DOM safe links | injection/sensitive tests V3; revisão estática UI | Padrões não cobertura adversarial universal; browser XSS real pendente; parcial |
| REQ-OBS-001 D bônus/P | structured logging/tools; /metrics | Logs suíte/independent probe; inspeção qualidade null | Métricas por processo; groundedness factual não medida; parcial |
| REQ-EVAL-001 D bônus/F/P | evaluation/run/live; development20/validation10; rubrica | offline-final.txt17 métricas estruturais1.0; artifact tests |14multi-turn definidos;3 repeats preparados, não executados; conjunto reservado visível em workspace; parcial |
| REQ-UI-001 P | app/static/index.html; browser_smoke.cjs | JS sintaxe pelo coordenador; revisão independente de DOM/papéis/ordenação | Nenhum browser/visual executado; workflow cliente/operador E2E pendente; parcial |
| REQ-INFRA-001 D/F/P | Dockerfile/Compose/nonroot/volume; scripts Windows; /health,/ready | Estático; independent probe503 missing index; dependency-install.txt | Docker/Windows/pins limpos/restart volume não executados; parcial |
| REQ-SDD-001 P | AUDIT_BASELINE/SPEC/ARCHITECTURE/ACCEPTANCE/TEST_PLAN/IMPLEMENTATION_PLAN/DEFECT_LOG | Especificação antes dos edits; ciclos e achados revisados; INDEPENDENT_REVIEW | Documentação não substitui integração; processo aplicado |
| REQ-SUB-001 D/P | README, PRE_SUBMISSION, DEMO_SCRIPT, ZIP | Empacotamento pelo coordenador após congelamento | GitHub e vídeo dependem do autor; pendente publicação/submissão |

Evidência histórica em evidence/historical não valida esta versão. Source excerpt presence não significa grounding. HTTP200 não significa resolução factual. Seed não representa fonte oficial. Integrações indisponíveis permanecem pendentes; critérios não foram reduzidos para aprovar.
