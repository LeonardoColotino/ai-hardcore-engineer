# Plano de testes

1. Baseline exato do ZIP: 92 testes, relatório preservado. Dependências usadas registradas pelo QA.
2. Unidade/contrato: plano, rotas, ferramentas, fakes de transportes, chunks e guardrails.
3. Integração: API/SQLite/índice reais; modelos/web simulados. Ownership, concorrência, rollback,
   duplicidade, resolução humana, memória, resultados parciais e falhas em cada posição.
4. HTTP socket local: processo uvicorn, autenticação, chat, handoff e reinício com arquivos temporários.
5. Retrieval: fixture sintética congelada, labels por chunk, recall@k/MRR/nDCG; comparar mesmos dados.
6. Runtime externo: Ollama e ingestão oficial no ambiente do usuário, versão/modelo/corpus registrados.
7. Semântica: rubricar intenção, sustentação, condições, completude, utilidade e idioma por afirmação.
   Não converter presença de fonte em groundedness. Revisão de agente não é revisão humana.
8. Browser/Docker: scripts reproduzíveis; skips/bloqueios não aprovam gates críticos.

QA criou casos antes de ajustar implementação e registrou hash. Depois de falhas usadas na correção,
esses casos são regressões, não holdout inédito. Nenhum teste foi removido para obter suíte verde.
Adaptações de contrato estão em evidence/current/QA_REVIEW.md.
