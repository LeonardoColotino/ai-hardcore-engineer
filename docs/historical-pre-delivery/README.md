# Getnet — V4 consolidada

API de suporte multiagente com Router/Planner, Knowledge (RAG + web), Support e Escalation. Interface cliente/operador, SQLite, autenticação, memória, tarefas limitadas, diagnóstico sanitizado e respostas parciais persistentes. Dados de suporte são fictícios. Não realiza operações financeiras.

Esta entrega combina o planejamento e transações da V4-final com recursos opcionais da V4-COMPLETO e regressões recuperadas da V3 1.4. Não implica uma nova nota nem validação de produção. Consulte [CONSOLIDACAO.md](CONSOLIDACAO.md), [VALIDATION_REPORT.md](VALIDATION_REPORT.md) e [LIMITATIONS.md](LIMITATIONS.md).

## Evidência do candidato

- Suíte Python e API HTTP real com SQLite e especialistas simulados: resultados atuais em `evidence/current/`.
- 17 cenários estruturais; não medem qualidade factual do modelo.
- Índice reconstruído de 14 snapshots oficiais herdados, sem nova consulta à internet.
- Recuperação de páginas em 12 perguntas expostas; não é avaliação inédita ou de evidência exata.
- Provedores e reranker neural têm testes de contrato simulados. Não foi executada inferência real desta consolidação.
- Docker, navegador e modelos reais precisam dos gates descritos no relatório. Resultados antigos ficam em `evidence/historical/` e não aprovam este release.

## Instalação local no Windows

Extraia em **pasta nova**. Não sobrescreva sua V3 ou as outras V4. Requer Python 3.12.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
notepad .env
```

No `.env`, configure `AUTH_SECRET` com pelo menos 32 caracteres e `DEMO_PASSWORD` com pelo menos 10. Para gerar um segredo:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
.\.venv\Scripts\python.exe scripts\init_demo.py
.\.venv\Scripts\python.exe -m scripts.rebuild_snapshot_index
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Abra http://127.0.0.1:8000. Clientes: `cliente1988`, `cliente2026`; operador: `operador`, na janela anônima. Todos usam a senha demo definida localmente. Não há senha pública. Se a porta 8000 estiver ocupada, pare apenas sua instância antiga ou use outra porta para esta instalação.

`LLM_PROVIDER=disabled` é o perfil inicial: ferramentas e trechos de contingência, sem modelo gerando respostas. O snapshot contém documentação temporal coletada anteriormente; não garante tarifas atuais. `--seed` é somente fixture sintética, não corpus oficial.

## Seu Ollama existente

Edite `.env`:

```dotenv
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_CHAT_MODEL=llama3.2:3b
OLLAMA_EMBED_MODEL=nomic-embed-text:latest
REQUEST_TIMEOUT_S=90
CHAT_BUDGET_S=180
LLM_MAX_OUTPUT_TOKENS=512
SUPERVISOR_MAX_STEPS=4
```

Reinicie o servidor. `ollama list` deve mostrar os modelos. Para atualizar fontes e usar embeddings Ollama:

```powershell
.\.venv\Scripts\python.exe -m app.rag.ingest --ollama-embeddings
```

Não é preciso trocar para embeddings neurais para testar contratos. O manifesto confere provedor/modelo/dimensão; reingira ao mudar o embedding. No notebook i5/16 GB, chamadas de planejamento e revisão podem levar tempo. Não envie repetidamente; a UI bloqueia envio concorrente. Aumentar timeout não comprova qualidade.

## Perfis opcionais recuperados

| Recurso | Configuração | Dependência / limite |
|---|---|---|
| Modelo local compatível | `LLM_PROVIDER=openai_compatible`, `LLM_BASE_URL=http://localhost:1234/v1`, `LLM_MODEL=...` | Endpoint próprio, schema JSON; `LLM_API_KEY` apenas se necessário |
| GGUF local | `LLM_PROVIDER=llama_cpp`, `GGUF_MODEL_PATH=...` | `requirements-local.txt`; pesos separados, execução deste release não verificada |
| Reranker aprendido | `RERANKER=cross_encoder` | `requirements-semantic.txt`; baixa pesos quando escolhido explicitamente |
| Autenticação OIDC | `AUTH_MODE=oidc` | RS256/JWKS HTTPS, issuer, audience e arquivo server-side de vínculo; login demo desativado |

APIs comerciais podem cobrar; assinatura ChatGPT não é chave de API. O padrão compatível é localhost. Não há chamada comercial nos testes. Para instalar GGUF/semântica, use os arquivos opcionais; a disponibilidade de wheels/modelos no Windows precisa ser validada localmente. Não são necessários na instalação básica.

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-local.txt --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu
.\.venv\Scripts\python.exe -m scripts.download_model
.\.venv\Scripts\python.exe -m pip install -r requirements-semantic.txt --extra-index-url https://download.pytorch.org/whl/cpu
```

A escolha de baixar pesos é sua. Hash de GGUF e revisão do reranker são fixados. Não confunda uso do reranker simulado em teste com execução dos pesos reais.

## Modos de resposta e retrieval

`KNOWLEDGE_ANSWER_MODE=evidence` (padrão): para produtos, seleciona trechos com IDs válidos e usa extração de procedimentos/condições quando documentados. Proveniência não prova pertinência, completude ou verdade. Perguntas gerais usam geração com evidência. `prose` permite a geração livre limitada por gates; requer revisão factual, não é melhoria comprovada.

`SUPERVISOR_EVIDENCE_REVIEW=true` revisa cobertura pública com saída estruturada quando o cliente oferece essa capacidade. Conflito/falha de revisão não publica a resposta como completa. Pode adicionar latência; não é juiz humano.

`RAG_RETRIEVAL_PROFILE=hybrid` combina cosseno e BM25 por RRF; `vector` e `lexical` permitem comparação. `RERANKER=none` evita dependências adicionais; `lexical` é scorer, `cross_encoder` é aprendido. Scores cosseno e fusão não são confiança factual. O perfil lexical usa score BM25 próprio: thresholds não são comparáveis entre perfis.

## Docker — projeto e volume novos

Não é necessário venv para executar no Docker. Mantenha o `.env` local preenchido. Na pasta desta entrega:

```powershell
docker compose -p getnet-v4-consolidado build
docker compose -p getnet-v4-consolidado run --rm api python scripts/init_demo.py
docker compose -p getnet-v4-consolidado run --rm api python -m scripts.rebuild_snapshot_index
docker compose -p getnet-v4-consolidado up -d
docker compose -p getnet-v4-consolidado ps
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```

Compose mantém banco/usuários/índice em volume próprio e usa `host.docker.internal:11434` para Ollama do Windows. Pare a aplicação antiga se ela ocupa 8000; não use `down -v`. Para substituir o snapshot por ingestão atual:

```powershell
docker compose -p getnet-v4-consolidado exec api python -m app.rag.ingest --ollama-embeddings
docker compose -p getnet-v4-consolidado restart api
```

`/health` é liveness; `/ready` verifica índice e disponibilidade/listagem do provedor, não geração bem-sucedida. O caso GGUF verifica arquivo/pacote, não carrega pesos no healthcheck.

## Verificação local e captura

```powershell
.\.venv\Scripts\python.exe -m pytest -q -p no:cacheprovider
.\.venv\Scripts\python.exe scripts/http_smoke.py
.\.venv\Scripts\python.exe -m evaluation.run --output evidence/current/structural-report.json
.\.venv\Scripts\python.exe -m evaluation.retrieval_compare
.\.venv\Scripts\python.exe -m evaluation.snapshot_retrieval
```

Com servidor e modelo real configurados:

```powershell
.\.venv\Scripts\python.exe -m evaluation.live --dataset development --output evidence/current/live-development.json
.\.venv\Scripts\python.exe -m evaluation.live --dataset validation --output evidence/current/live-validation.json
```

Informe a senha demo quando solicitada. Os datasets são históricos/expostos; formule casos novos antes de ajustar o candidato. Capture fontes completas e revise intenção, afirmações, condições, relevância e utilidade. Não chame HTTP 200/citações de grounding. Falhas/interrupções permanecem no JSON. Para Docker, execute captura no host ou use `--url http://127.0.0.1:8000` dentro do container e grave saída em `/state/`.

## API e fluxo

`POST /auth/login`, `POST /chat` com `{message, user_id?, session_id?, idempotency_key?}` e Bearer; identidade vem do token. `/sessions`, `/tickets`, `/tickets/{id}/reply`, `/traces/{request_id}` e `/metrics` têm ownership/papéis. `/docs` descreve contratos. Não use retry com outra chave para a mesma operação sem entender o estado anterior.

Router/Planner → tarefas (máximo 4) → Support/Knowledge → revisão e uma recuperação adicional oficial quando permitida → composição preservando partes válidas → ticket nas partes não resolvidas. Diagnóstico sanitizado alimenta Knowledge; dados privados não vão à busca pública. Ticket ativo pausa tools até resolução. SQLite e coordenação são single-process.

## Entrega

[CONSOLIDACAO.md](CONSOLIDACAO.md) lista origens e decisões. [ROTEIRO_VIDEO.md](ROTEIRO_VIDEO.md) orienta gravação pessoal. `demo/historical-v4-walkthrough.mp4` é somente ilustração antiga legendada, não vídeo deste candidato nem gravação do autor. Consulte os gates pendentes antes da submissão.
