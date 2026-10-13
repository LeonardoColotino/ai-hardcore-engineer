# Defect log — QA separado

Baseline executado 2026-10-12 em Linux Python3.12: 64 testes preexistentes passaram; 7 regressões novas falharam. Comando `python -m pytest -q`; saída integral `evidence/qa-baseline.txt`. FastAPI0.143.0; instalação dos pins integrais bloqueada inicialmente em rede403. Não foi modelo real. JSON histórico anexado lido integralmente: evidência anterior, não candidato.

| ID | Requisito/severidade | Reprodução | Esperado / observado baseline | Estado |
|---|---|---|---|---|
| QA-01 | REQ-ROUTE-001 alta | Classifier support0.99; Gostaria de aderir ao Link | Knowledge / Support | Corrigido A; revalidado qa-final 77 verdes |
| QA-02 | REQ-HITL-001 alta | Classifier support0.99; atendente humano | Escalation direta / Support | Corrigido A; revalidado qa-final 77 verdes |
| QA-03 | REQ-ROUTE-001 alta | Classifier support0.99; taxas do Link | Knowledge / Support | Corrigido A; revalidado qa-final 77 verdes |
| QA-04 | REQ-HITL-001 alta | POST chat humano, GET ticket | OPEN, ticket_created=true, sem agentes duplicados / false, recommended, texto contraditório | Corrigido A; revalidado qa-final 77 verdes |
| QA-05 | REQ-OBS-001 média | web retorna erro, pergunta euro | Knowledge web_search seguido Escalation / Knowledge human_handoff | Corrigido A; revalidado qa-final 77 verdes |
| QA-06 | REQ-GROUND-001 alta | Conectividade; RAG Conta Digital score.99, web offline | Não resolver, ticket / escalated=false | Corrigido A; revalidado qa-final 77 verdes |
| QA-07 | REQ-MEM-001 alta | Link → Obrigado → E para aderir a ele? | Link preservado Knowledge / products vazio, escala indevida | Corrigido A; revalidado qa-final 77 verdes |

Reprodução codificada em `tests/integration/test_audit_regressions.py`, antes dos ajustes. QA não altera produção. Critérios não reduzidos, nenhum skip/xfail adicionado. Tickets definitivos são fechados somente após reexecução candidata correspondente.

## Bloqueios externos

Modelo local Ollama e notebook Windows ausentes neste ambiente: grounding/relevância/utilidade e p95 real não aprovados por offline. Docker/browser conforme revisão final, não inferir aprovação de leitura. Dataset desenvolvimento20/validação10 congelado, 14 multi-turn. Disponível ao implementador no pacote; não alegar holdout oculto ou avaliação humana.

## Ciclo 1

`evidence/qa-cycle1.txt`: 70 passam, 2 falham. Sete novas regressões resolvidas. QA fortaleceu teste preexistente de contratação para exigir abstention explícita, origem Knowledge, produto correto e ticket: seed só contém instrução de uso, portanto o aceite anterior de resolução contraria REQ-GROUND-001. Não é relaxamento de expectativa. Falhas: metadata abstention descartada no handoff e referência criar link. Ambos encaminhados A.

## Ciclo 2 direcionado

`evidence/qa-cycle2-targeted.txt`: 9 passam, 1 falha. Novo QA-08 REQ-MEM-001, alta: Link → correção Pix → Como ele funciona?; estado Pix selecionado é indevidamente substituído por catálogo de produtos mencionados em fallback. Esperado manter seleção explícita Pix. Encaminhado A antes da correção. Exceção tool confirma trace limpo e nova sessão não herda produto.

## Ciclos finais / transparência de QA

QA-08 corrigido: referência após correção preserva seleção Pix. QA-09 (validador, REQ-GROUND-001 alta): disclaimer “serviços contratados” e CTA “Quero contratar” eram aceitos como procedimento; reprodução direta do validador anterior à correção, dois testes QA negativos adicionados. Corrigido A e revalidado.

`qa-cycle3.txt` e `qa-cycle4-targeted.txt` registram falha do novo teste de tracing por DTO errado (ChatRequest interno sem session_id). QA corrigiu fixture para Chat da API e execução direta no mesmo ContextVar; não era defeito de produção, expectativa inalterada.

Final após freeze: `evidence/qa-final.txt` **77 passed, 1 warning, 5.14s**. `evidence/offline-final.txt`: 17 cenários legados passam roteamento/tools/presença/trechos/falhas. Hash/ambiente em `evidence/qa-final-manifest.json`. Aviso Starlette/httpx permanece documentado, sem instalar outra dependência para silenciá-lo. Não aprova factualidade ou latência de Ollama. Nenhum skip/xfail.
