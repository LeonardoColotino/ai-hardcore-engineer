> Documento de arquitetura/base herdado. Revisões 1–6 estão consolidadas; para resultados e limitações atuais, consulte README.md e VALIDATION_REPORT.md.

# Arquitetura consolidada

API autenticada → Supervisor com memória/ownership/idempotência → Router/Planner tipado → tarefas Support/Knowledge/Escalation → revisão pública estruturada quando habilitada → no máximo uma recuperação oficial adicional → composição preservando resultados → ticket persistente para partes não resolvidas.

Support verifica identidade no servidor; cadastro/repasse/transação/diagnóstico são ferramentas de leitura sintéticas. Diagnóstico enum sanitizado é a dependência consumida por Knowledge; fatos privados não são reenviados à busca. Knowledge utiliza retrieval vetorial/BM25/RRF, relevância, reranking opcional e seleção de evidências ou geração com gates. Permissões e limites são políticas do servidor.

Dados: SQLite para mensagens/estado/tickets/traces/feedback/reservas; NumPy+JSON+manifesto para índice pequeno; snapshots temporais oficiais e fixtures de teste separados. Provedores: disabled, Ollama, OpenAI-compatible e GGUF opcional. Autenticação demo ou OIDC RS256 com mapa server-side.

Revisão do LLM pode marcar complete/incomplete/conflict; não concede tools. Falha/conflito não vira resposta completa. Citação valida proveniência, não factualidade. Readiness é diagnóstico de configuração/disponibilidade, não teste de qualidade.

Uma instância/worker; coordenação distribuída, IdP real e filas externas não implementados. Serviços comerciais e frameworks adicionais não são necessários para os contratos locais.
