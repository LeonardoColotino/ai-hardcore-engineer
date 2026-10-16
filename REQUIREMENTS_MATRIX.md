> Documento de arquitetura/base herdado. Revisões 1–6 estão consolidadas; para resultados e limitações atuais, consulte README.md e VALIDATION_REPORT.md.

# Matriz de requisitos e evidências

| Requisito | Implementação | Verificação atual | Limite |
|---|---|---|---|
| Agentes/plano | router, planner, specialists | testes de tarefas e falhas parciais | modelo simulado |
| RAG/web | retriever, BM25/RRF, gates, web privacy | testes e retrieval página/fixture | não semântica live |
| Tools próprias | cadastro, repasse, transação, terminal | integração com dados sintéticos | não conta real |
| Memória/ownership | supervisor, Store | testes multi-turn/isolamento | âncoras finitas |
| HITL | tickets e operador | API/SQLite e testes de concorrência | operador demo |
| Provedores | Ollama/compatível/GGUF | contratos/schema/truncamento | sem pesos reais nesta rodada |
| OIDC | RS256/JWKS/mapa | assinatura RSA real, JWKS simulado | sem IdP externo |
| Observabilidade | traces/usage/feedback | testes e smoke | single-process |
| Interface | chat/operador | código e script browser | E2E pendente nesta rodada |
| Docker/CI | non-root/volumes/workflow | scripts entregues | execução pendente |
| Vídeo | roteiro e vídeo antigo identificado | não é gravação pessoal | candidato deve gravar |
