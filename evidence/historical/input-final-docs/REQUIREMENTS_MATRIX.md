# Matriz de requisitos do candidato

| Requisito | Código | Teste/evidência atual | Estado e limite |
|---|---|---|---|
| Router + Knowledge + Support + Escalation | app/agents, orchestration/planner.py | test_router, test_final_qa; final-pytest | Implementado; LLM simulado nos testes |
| Plano limitado e resultados parciais | models/plan.py, planner.py | test_final_qa: ordens/falhas 1º/meio/último | Aprovado estruturalmente; generalização live pendente |
| Cooperação terminal → conhecimento | terminal_diagnosis.py, planner.py | test_v3, test_final_qa | Diagnóstico sintético sanitizado consumido; não lê terminal real |
| API POST/message/user_id | api/routes.py, security.py | test_api, http-smoke.json | Aprovado HTTP real; identidade deriva do token |
| RAG ingestão/índice/geração | rag/*, knowledge.py | test_rag_release, test_rag, test_live_regressions | Transporte/modelos mockados; corpus oficial atual pendente |
| Busca pública sem dados de conta | public_query.py, web_search.py | test_final_qa | Gate testado; não prova detecção de toda PII |
| Duas ou mais tools de suporte | tools/{customer_lookup,payment_status,transaction_lookup,terminal_diagnosis}.py | test_tools, test_final_qa | Dados fixos fictícios; sem escrita financeira |
| Memória e isolamento | supervisor.py, persistence.py | test_v3, test_audit_regressions | Âncoras persistentes; memória semântica ilimitada não implementada |
| Handoff e operador | persistence.py, routes.py, static/index.html | concorrência/rollback QA, HTTP real | Aprovado no backend; browser E2E pendente |
| UI português/mobile/Markdown seguro | static/index.html | inspeção e script browser_smoke.cjs | Implementado; browser binário indisponível |
| Traces/feedback/tokens | persistence.py, routes.py, services/llm.py | QA ownership; suíte final | Persistência local; tokens só quando provedor reporta |
| Auth/RBAC/ownership | security.py | test_api/test_v3/test_final_qa | Demonstração PBKDF2/HMAC; IdP corporativo não integrado |
| Docker non-root/volumes/CI | Dockerfile, compose, .github/workflows | scripts/docker_smoke.py | Inspecionado, execução Docker/GitHub pendente |
| Retrieval comparativo | evaluation/retrieval_compare.py | retrieval_comparison.json | 6 consultas sintéticas; sem ganho observado, não mede factualidade |
| Avaliação factual por afirmação | evaluation/live.py, RUBRIC.md | testes checkpoint, datasets | Captura pronta; revisão factual live pendente |
| Provedores | services/llm.py, embeddings.py | test_llm_transport | Ollama implementado; fake nos testes; adaptador OpenAI-compatible não incluído |
| Regressões históricas | tests herdados + QA | baseline92 → final122 | 3 arquivos posteriores não anexados; sem reconstrução fictícia |
| README/instalação/vídeo | README, COMECE_AQUI, DEMO_SCRIPT | comandos/revisão | Roteiro entregue; gravação pessoal e publicação pendentes |

Os caminhos de evidência referem-se a `evidence/current/`. Aprovação estrutural não é aprovação semântica.
