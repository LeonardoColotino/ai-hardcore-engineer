# Plano de teste atual

Comando: python -m pytest tests -q -p no:cacheprovider.

248 casos cobrem contratos e falhas de router, guardrails, dados autenticados, fontes, seleção, preservação de procedimentos, atribuição de produto, fragmentos e abstenção, plano limitado, contexto por sessão/dono, respostas parciais, idempotência, colaboração, handoff e autorização. Há fixtures reproduzindo respostas incorretas capturadas com Ollama; essa reprodução é simulada, não nova inferência.

Avaliação offline: python -m evaluation.run --output evidence/current/offline-report.json. São 17 cenários estruturais, não nota de qualidade.

Captura real: scripts.compare_answer_modes usa 3 perguntas de desenvolvimento em dois modos sobre a mesma recuperação e registra antes/depois da revisão e tempo. Separar resultados de teste/produção, não ocultar falhas e não extrapolar a amostra para todas as perguntas.

Confirmação manual do usuário: procedimento/continuação, capital Argentina, pagamento demonstrativo, mensagem de operador e encerramento do ticket. Não expandir o roteiro como se fossem casos já aprovados. Novos ambientes/provedores exigem nova validação.
