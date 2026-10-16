# Getnet · sistema multiagente

Candidato evoluído do snapshot V3 fornecido: chat em português, Router/Planner,
Knowledge com RAG e busca web, Support com cadastro/repasse/transações/terminal,
Escalation com fila e resposta humana. API autenticada, sessões SQLite, interface
cliente/operador, planos limitados, resultados parciais, traces e feedback.
Dados de suporte são fictícios e suas datas são fixas. Não realiza operações financeiras.

## Evidência atual

Consulte `VALIDATION_REPORT.md` e `evidence/current/` para os resultados finais.
- API HTTP/socket e SQLite: executados localmente, incluindo reinício e atendimento humano.
- Testes de engenharia: especialistas/provedores simulados; não comprovam factualidade de LLM.
- Retrieval: comparação em fixture sintética congelada, sem comprovação em corpus oficial live.
- Ollama, Docker, browser E2E e revisão factual live: dependem das condições registradas no relatório.
- Evidências recebidas de outras versões ficam em `evidence/historical/`; não aprovam este candidato.

## Começar no Windows PowerShell

Extraia o ZIP em uma pasta nova. Abra PowerShell na pasta que contém este README.
Não copie a instalação nova sobre sua versão anterior nem seus bancos.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows.ps1
notepad .env
```

Preencha `AUTH_SECRET` com um segredo aleatório de pelo menos 32 caracteres e
`DEMO_PASSWORD` com senha de pelo menos 10 caracteres. Exemplo para gerar o segredo:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
.\.venv\Scripts\python.exe scripts\init_demo.py
.\.venv\Scripts\python.exe -m app.rag.ingest --seed
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

Abra http://127.0.0.1:8000 e entre como `cliente1988`, `cliente2026` ou `operador`,
com a senha configurada. Use uma janela anônima para o operador. `/docs` contém os
contratos HTTP. O perfil inicial `LLM_PROVIDER=disabled` usa contingência extrativa;
o seed é sintético e **não é informação comercial oficial verificada**.

## Conectar seu Ollama

Os modelos já utilizados são `llama3.2:3b` e `nomic-embed-text:latest`.
Execute `ollama list` e confirme ambos. O script de conexão não baixa pesos sem decisão sua.

```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\connect_ollama_windows.ps1
```

No `.env`, configure `LLM_PROVIDER=ollama`, `OLLAMA_BASE_URL=http://localhost:11434`,
`OLLAMA_CHAT_MODEL=llama3.2:3b` e `OLLAMA_EMBED_MODEL=nomic-embed-text:latest`.
Para CPU, aumente `REQUEST_TIMEOUT_S` e `CHAT_BUDGET_S` conforme a medição local;
por exemplo 90 e 180 segundos. O orçamento inclui espera pela sessão e etapas;
timeout de socket não cancela instantaneamente uma operação bloqueada.

```powershell
.\.venv\Scripts\python.exe -m app.rag.ingest --ollama-embeddings
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

A ingestão sem `--seed` consulta apenas hosts Getnet permitidos. Falhas ficam nos logs.
Troca de modelo/provedor/dimensão exige reconstrução do índice. `/ready` verifica
precondições; estar pronto não prova qualidade semântica. Preserve o manifesto do corpus.

## Docker (sem venv no host)

Configure `.env` antes. O container usa usuário não-root e volume `/state`.

```powershell
docker compose build
docker compose run --rm api python scripts/init_demo.py
docker compose run --rm api python -m app.rag.ingest --ollama-embeddings
docker compose up -d
docker compose logs -f api
```

No container, `localhost` é o próprio container. Compose usa `host.docker.internal`
para o Ollama do Windows. Para demonstração offline, substitua a ingestão por
`python -m app.rag.ingest --seed` e mantenha `LLM_PROVIDER=disabled`.
Não use `docker compose down -v` se quiser conservar o volume.

## Testes e avaliação

```powershell
.\.venv\Scripts\python.exe -m pytest -q
.\.venv\Scripts\python.exe -m evaluation.run
.\.venv\Scripts\python.exe -m evaluation.retrieval_compare
.\.venv\Scripts\python.exe scripts\release_manifest.py
.\.venv\Scripts\python.exe scripts\docker_smoke.py
```

`evaluation.run` é a avaliação estrutural herdada do orquestrador de chamada direta,
com web fake e LLM desabilitado; a suíte API cobre o supervisor novo. Os campos com
sufixo `accuracy` no runner legado são contagens estruturais, não aprovação factual.
A comparação retrieval usa fixture sintética e IDs exatos de chunks; não misture esses
números com resultados de corpus oficial ou outro modelo.

Com servidor/Ollama reais ativos, capture e depois revise afirmações e fontes:

```powershell
.\.venv\Scripts\python.exe -m evaluation.live --dataset development --repetitions 1 --output evidence/current/live-development.json
.\.venv\Scripts\python.exe -m evaluation.live --dataset validation --repetitions 1 --output evidence/current/live-validation.json
```

A captura registra falhas/interrupções e hashes. `generation_kind=llm` distingue inferência
retornada de fallback; HTTP 200 e URL presente não aprovam intenção, condições ou sustentação.
Use `evaluation/RUBRIC.md`. Casos já usados em correções deixam de ser inéditos.

## Arquitetura e limites

Veja `ARCHITECTURE.md`, `SPEC.md`, `REQUIREMENTS_MATRIX.md` e `TEST_PLAN.md`.
O notebook pode executar um processo; SQLite e locks locais não constituem arquitetura
multi-réplica. Não foi adicionado IdP corporativo, provedor pago, reranker neural ou streaming
para ampliar escopo sem evidência. O limite de tarefas evita loops e não concede permissões.

Para a entrega do desafio, publique você o repositório e grave o percurso em `DEMO_SCRIPT.md`.
Nenhuma publicação ou gravação pessoal foi realizada por este trabalho.
