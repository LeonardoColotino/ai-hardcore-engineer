# Validação — V4 consolidada, 2026-10-15

As aprovações abaixo pertencem somente ao escopo executado nesta consolidação. Não há nota estimada nem aprovação global de produção.

| Gate | Resultado atual | Evidência |
|---|---|---|
| Suíte Python | **193 passed, 1 warning, 8,22 s** | `evidence/current/pytest-final.txt`, `pytest.xml` |
| Dependências instaladas | sem conflitos declarados | `evidence/current/pip-check.txt` |
| Sintaxe Python e script browser | aprovadas | compileall e node --check |
| HTTP real / Uvicorn / SQLite | idempotência, ownership, operador e reinício aprovados | `evidence/current/http-smoke.json` |
| Avaliação estrutural offline | 17 casos, métricas de contrato 1,0 | `evidence/current/structural-report.json` |
| Retrieval sintético | 6 consultas, três perfis; recall@3/MRR/nDCG@3 1,0 | `evidence/current/retrieval-synthetic.json` |
| Reconstrução de corpus | 14 snapshots herdados → 23 chunks, hashing | `app/data/vector_store/manifest.json` |
| Retrieval de páginas oficiais herdadas | 12 perguntas expostas; recall de páginas/MRR 1,0 sem e com scorer lexical | `evidence/current/snapshot-page-retrieval*.json` |
| Provedores e OIDC | contratos simulados; assinatura RSA local real | `tests/integration/test_consolidation.py` |
| Reranker neural / pesos GGUF | **não executados**: opcionais não instalados | `evidence/current/runtime-status.json` |
| Inferência real / ingestão oficial atual | **pendentes**: Ollama indisponível nesta rodada | `evidence/current/runtime-status.json` |
| Docker / CI hospedada | **pendentes**: CLI ausente; workflow não publicado | script e workflow entregues |
| Browser E2E | **pendente**: launch Playwright falhou por binário ausente | `evidence/current/runtime-status.json` |
| Revisão factual humana e validação inédita | **pendentes** | capturar/revisar no perfil final |

## Comandos executados

```text
python -m pytest -q -p no:cacheprovider --junitxml=evidence/current/pytest.xml
python -m pip check
python scripts/http_smoke.py
python -m evaluation.run --output evidence/current/structural-report.json
python -m evaluation.retrieval_compare --output evidence/current/retrieval-synthetic.json
python -m scripts.rebuild_snapshot_index
python -m evaluation.snapshot_retrieval --reranker none
python -m evaluation.snapshot_retrieval --reranker lexical --output evidence/current/snapshot-page-retrieval-lexical.json
python -m compileall -q app scripts evaluation tests
node --check scripts/browser_smoke.cjs
```

Suíte de origem final: 122 testes. Regressões V3 recuperadas: 57 casos adicionais. Novos contratos da consolidação: 14 casos. Nenhum teste da base final foi apagado. Duas fixtures de transporte antigas foram adaptadas; o teste de geração livre declara o modo prose. Detalhes em CONSOLIDACAO.md.

O primeiro merge teve quatro falhas: fixtures antigas de HTML não modelavam DNS/streaming, ordem dos gates de informação atual e modo de geração numérica. As correções e reruns estão preservados. A fixture de informação atual do avaliador offline antes não continha data/medição; foi substituída por conteúdo explicitamente fictício compatível com a política. Não se enfraqueceram os gates de produção nem se modificaram as expectativas do dataset para ocultar falha.

## Interpretação correta

- O smoke HTTP usa banco real, dados sintéticos e LLM/web desativados. Não prova RAG live ou geração.
- Recall de página mede encontrar URL esperada em perguntas já expostas. Não é recall de afirmação nem qualidade factual, e não demonstra ganho neural.
- Corpus reconstruído de snapshots herdados: nenhuma nova coleta. IDs/chunks mudaram; os resultados por chunk antigos não aprovam este índice.
- GGUF, API compatível e CrossEncoder têm testes com inferência simulada. O teste OIDC verifica assinatura real, mas simula JWKS e provisionamento.
- Revisão estruturada do modelo é um controle auxiliar, não validação humana nem prova universal de entailment.
- Pacotes básicos já estavam no ambiente; PyJWT foi acrescentado e pip check passou. Uma instalação limpa no Windows/Docker ainda precisa ser validada.
- Não houve agente delegado independente nesta consolidação. QA/Validator dos inputs estão no histórico e não aprovam este candidato novo.

Warning: depreciação Starlette TestClient/httpx; não foi ocultado. Capturas antigas de modelo/navegador estão identificadas como históricas, não evidência desta versão.

## Próximo gate local

Executar Docker e browser, conectar modelo real, identificar corpus/modelo/hash e capturar perguntas novas. Revisar afirmações, pertinência, condições e procedimentos completos. Corrigir falhas antes de publicar. Preservar a V3 publicada enquanto isso.
