# Relatório final — candidato 2026-10-15

## Resultado por gate

| Gate | Parecer | Evidência |
|---|---|---|
| Instalação com dependências fixadas | aprovado | `resume-install.txt`, `pip-check.txt`; Python 3.12.14 |
| Suíte aplicável | aprovado | `final-pytest.txt`: **122 passed**, 1 warning, 7.97s |
| Revisão delegada independente | aprovado no escopo executado | `VALIDATOR_REVIEW.md`, rerun 122/122, 7.96s |
| API/SQLite local real | aprovado | `http-smoke.json`: idempotência, ownership, operador e restart |
| Avaliação estrutural herdada | aprovado após atualização de contrato | 17 casos, `structural-evaluation.txt` e `evaluation/report.json` |
| Retrieval de fixture congelada | aprovado no escopo sintético | 6 queries, perfis vector/lexical/hybrid; todos recall@3/MRR/nDCG@3=1; amostra simples sem ganho demonstrado |
| Docker operacional/CI hospedada | pendente por bloqueio | CLI/daemon ausentes; scripts/CI entregues, não executados remotamente |
| Browser E2E | pendente por bloqueio | Playwright sem binário Chromium/Chrome; `runtime-blockers.json` |
| Ollama/embeddings/rede oficial atuais | pendente por bloqueio | Ollama inacessível; não houve inferência real ou ingestão live do candidato |
| Qualidade semântica/factual live | pendente por bloqueio | Requer execução do perfil/corpus final e revisão por afirmação |
| Gravação pessoal e link GitHub | pendente externo | Roteiro disponível; nenhuma gravação/publicação realizada |

Não há aprovação global de produção nem estimativa de nota. Há código implementado e engenharia
verificada, com limites de runtime/qualidade descritos. Warning: depreciação Starlette TestClient/httpx;
a suíte passa com as versões fixadas, não se alterou dependência apenas para ocultar aviso.

## Execuções e correspondência

Todos os arquivos citados sem prefixo estão em `evidence/current/`. `release-manifest.json`
identifica arquivos e dependências efetivamente empacotados. `http-smoke.json` registra o hash do código
`app/` executado. O último smoke é API real com dados sintéticos e **LLM/web desabilitados**, sem índice:
ele não prova RAG factual. O runner retrieval cria índice real temporário com fixture sintética.

Comandos executados: `python -m pip install -r requirements.txt`, `python -m pip check`,
`python -m pytest -q`, `python scripts/http_smoke.py`, `python -m evaluation.run`,
`python -m evaluation.retrieval_compare`. O Validator repetiu testes e smoke de modo independente.
Durante retomada, pacotes do ambiente haviam sido reiniciados; foram reinstalados e os testes repetidos.

Baseline do snapshot anexado: **92 testes**, não os 149 mencionados no prompt. Os arquivos
`test_second_live_regressions.py`, `test_third_live_regressions.py` e `test_fourth_live_regressions.py`
não vieram no ZIP. V4 e `live_development_final.json`/`live_validation_final.json` também não vieram.
Há capturas com outros nomes no snapshot; foram mantidas como históricas, sem aprovação transferida.

A avaliação estrutural detectou 16/17 na seleção de ferramenta porque c05 ainda esperava
`customer_lookup` para diagnóstico. O novo contrato executa `terminal_diagnosis` após verificar cliente.
O resultado anterior está em `structural-before-terminal-contract.json`, e o dataset original está
no histórico. Foi atualizada apenas a tool esperada de c05; cenário preservado. Resultado: 17/17 na
seleção de ferramenta. Isso não mede resposta correta ao problema de conexão de um cliente real.

## Mudanças e regressões

- Plano tipado e limitado; falhas por tarefa preservam as partes válidas e geram protocolo.
- Diagnóstico sanitizado substitui envio do texto privado do suporte ao Knowledge.
- Ticket ativo impede bot de executar tools; resposta humana atômica, ownership e corrida testados.
- Idempotência persistente por chave; reservas interrompidas retornam conflito para reconciliação segura.
- UI conserva histórico, inclui conversa no operador, avaliação autenticada e prevenção de envio duplicado.
- Ingestão valida hosts/redirects/tamanho e preserva blocos; índice vincula hashes/provedor/modelo/dimensão.
- Prompt deixa de impor 45 palavras/sem passos; gates numéricos/comparação são limitados e não entailment.
- Traces persistentes minimizados, versões de prompt, tokens reportados ou desconhecidos.

Nenhum teste herdado foi excluído. Duas adaptações de contrato/fixture estão documentadas no relatório QA.
O índice público antigo sem manifesto foi arquivado e não é carregado por padrão como corpus atual.

## Limites remanescentes

Planner offline depende de regras; planejamento semântico Ollama não foi executado aqui. Replanejamento
é uma tentativa oficial limitada; contradições complexas, completude de procedimentos e idioma exigem
revisão factual real. Não há reranker neural, provedor OpenAI-compatible, IdP corporativo ou avaliação
contínua calibrada por humano. Estes itens não são apresentados como implementados.

A proteção de DNS é pré-validação, sem pinagem de IP; deadlines não cancelam instantaneamente bloqueios
síncronos. Memória usa âncoras finitas; SQLite/locks/métricas/rate limit são single-process. Não há alegação
de imunidade a injection/PII, escala distribuída ou certificação. Documentação de limites não substitui
validação: execute os gates externos antes de declarar candidato integralmente aprovado.
