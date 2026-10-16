# QA / Test Plan — candidato V3 evoluído

Responsável: agente B real, separado de implementação e revisão. Critérios congelados antes das correções de produção em `SPEC.md` e `ACCEPTANCE_CRITERIA.md`. Testes sintéticos verificam contratos e estados, nunca qualidade semântica real.

## Ambientes e níveis

- Python 3.12 Linux; instalação integral em `evidence/dependency-install.txt`. Baseline/ciclos FastAPI 0.143.0; instalação integral dos pins bloqueada por rede403 ao buscar uvicorn. Windows 3.12.10 permanece execução externa pendente.
- Unitários: roteamento com classifier adversarial, guardrails, tools, chunking e transporte.
- API: TestClient, identidade assinada de fixture, banco/índice temporários; sessão e ticket persistentes, papéis e cruzamento de usuários.
- Regressões adicionadas **antes da correção**: `tests/integration/test_audit_regressions.py`; baseline 7 falhas documentadas, sem skip/xfail.
- Browser: coordenação/validador executam UI real se disponível; HTML 200 não aprova layout.
- Docker/Ollama: integrações reais separadas, não simuladas; execução local automatizada necessária onde indisponíveis.

## Matriz de cenários QA

| Requisito | Positivo | Negativo / adversarial | Evidência |
|---|---|---|---|
| REQ-ROUTE-001 | Conhecimento produto e humano explícito | LLM retorna support com 0.99 para adesão, taxas, humano | test_clear_policy_overrides_misleading_llm |
| REQ-MEM-001 | Link → Obrigado → paráfrase aderir | Nova sessão, alheia, inexistente e produto ambíguo | test_memory_paraphrase_after_intermediate_message, test_v3 |
| REQ-GROUND-001 | Fonte aplicável e contexto preservado | Score .99 Conta Digital para problema de conectividade | test_high_score_wrong_product_not_resolution |
| REQ-HITL-001 | Ticket OPEN e ciclo operador/histórico/CLOSED | Metadata false, dono concorrente, saltos de estado | test_persisted_handoff_metadata_truth, test_handoff_cycle_and_authorization |
| REQ-OBS-001 | Etapa Knowledge mostra web_search executado | Handoff falsamente atribuído à busca | test_knowledge_failure_stage_tool_is_not_handoff |
| REQ-ENC-001 | Dados/captura UTF-8 com acentos | Codificação implícita Windows | runner explícito UTF-8 e teste roundtrip |
| REQ-PERF-001 | Tempos por etapa, orçamento explícito | Timeout/provider falhando | failure/test_llm_transport; latência real pendente |

## Avaliação congelada

`development_dataset.json`: 20 casos D01–D20. `validation_dataset.json`: 10 casos V01–V10. 14 casos multi-turn no total. D01–D08 correspondem ao histórico L1–L8. Seleção feita pelo QA antes dos ajustes. O conjunto reservado é entregue com o código: não alegar holdout secreto nem independência se o implementador acessar para ajustar respostas. Dataset não inclui respostas comerciais fixas, requer revisão das fontes reais.

Repetir cada fluxo crítico 3 vezes via runner live. Capturar falhas e tentativas no denominador. Avaliador humano ou IA identificado; notas 0 incorreto, 1 parcial, 2 atende com justificativa por dimensão. ≥90% respostas úteis fundamentadas onde evidência suficiente; ≥95% roteamento/tools, zero tool financeira indevida em produto, zero dimensão crítica 0 e médias groundedness/relevância ≥1.8/2. Fallback/abstenção não contam automaticamente como utilidade.

## Comandos

`python -m pytest -q` (todos); `python -m evaluation.run` (offline fixtures); `python -m evaluation.live --dataset development --repetitions 3` e `--dataset validation --repetitions 3` (HTTP real). Revisar saídas brutas e fontes completas; os runners não autoaprovam semântica. Modificação posterior invalida evidências afetadas.
