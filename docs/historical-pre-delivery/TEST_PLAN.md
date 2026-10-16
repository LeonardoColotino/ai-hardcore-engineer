# Plano de testes consolidado

1. Suíte herdada final + regressões V3 recuperadas + contratos dos novos provedores/OIDC/reranker/revisão.
2. HTTP real em processo Uvicorn/SQLite: login, idempotência, ownership, ticket, operador, traces e reinício; LLM/web desativados.
3. 17 casos estruturais: seed e web simulados; não factualidade.
4. Retrieval: fixture sintética exata e 12 perguntas históricas em páginas de snapshots oficiais. Labels expostos; não held-out independente.
5. Gates locais pendentes: Docker, browser, inferência real e revisão semântica por afirmação; use scripts do README.

Fixtures de transporte foram atualizadas para fetch protegido, sem retirar asserções. Geração livre e seleção têm contratos diferentes testados separadamente. Unknown usage é None; schema/truncamento falham de forma segura. Nenhum revisor humano participou desta consolidação.
