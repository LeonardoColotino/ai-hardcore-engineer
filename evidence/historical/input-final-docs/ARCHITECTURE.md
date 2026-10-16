# Arquitetura e decisões

`POST /chat` autentica cliente, valida user_id e ownership, reserva chave idempotente opcional,
e entra no supervisor com lock por sessão e deadline incluindo fila. Guarda de entrada precede
planejamento. Ticket ativo mantém recepção de mensagens e suspende ferramentas.

Plano tipado permite knowledge/support/escalation e dependência somente de tarefa anterior;
limite configurável até 4 etapas. Perguntas simples usam rota curta. Mensagens compostas usam
planner estruturado local quando habilitado; fallback por cláusulas é limitado e não promete
compreensão semântica universal. Identidade nunca faz parte dos argumentos do planner.

Cada especialista produz resultado e revisão operacional. Falha é isolada por tarefa; montagem
determinística conserva as partes válidas e adiciona limitação/protocolo. Não há seleção por
maior confidence, média factual ou nova chamada de síntese capaz de apagar resultados válidos.
Falta de evidência permite uma mudança de estratégia para busca restrita oficial, sob orçamento.
Contradições difíceis sem evidência suficiente continuam dependentes de revisão humana.

Terminal usa telemetria **sintética** tipada e produz diagnóstico público allowlisted. Knowledge
recebe apenas esse diagnóstico, nunca cadastro, valor ou texto privado do suporte. Toda busca web
passa por gate adicional no servidor. O gate é conservador, não detector perfeito de toda PII.
Não é enviado histórico completo a provedores para formatação. Ollama local é o runtime integrado.

Memória: SQLite armazena mensagens, produto selecionado, candidatos, últimos produtos e ferramenta
de conta. Janela de 12 mensagens é contada; resolução contextual usa âncoras, não memória semântica
ilimitada. Mudança explícita de assunto limpa âncora; ambiguidade entre produtos pede esclarecimento.

RAG: HTTPS oficial → validação de DNS/redirects/bytes → extração de blocos → chunks com metadados
→ embeddings/hash/modelo → índice NumPy persistente → recuperação → filtros → resposta em português.
Fontes são dados não confiáveis. Gates de números/características/comparação são verificações
limitadas, não entailment completo. Contingência literal é identificada. Corpus temporal não garante
preços atuais. Validação DNS não fixa o IP da conexão: não é proteção universal contra DNS rebinding.

HITL: OPEN → IN_PROGRESS → RESOLVED → CLOSED. SQLite BEGIN IMMEDIATE torna resposta e mensagem humana
atômicas; política evita dois tickets ativos no mesmo turno/sessão. Apenas operador designado ou admin
pode continuar o ticket. Resolução libera bot. Não existem escritas financeiras ou autorização por texto.

API de traces persiste projeção operacional sem queries/respostas privadas. Ownership/RBAC protegem
traces e histórico; feedback pertence ao dono da requisição. Métricas p50/p95 são locais por processo,
separadas de qualidade. Tokens ausentes permanecem desconhecidos. Front usa textContent e Markdown
mínimo seguro, bloqueia envio duplicado, chave idempotente e epoch para respostas fora de sessão.

SQLite e locks são adequados ao demonstrador single-process; para múltiplas réplicas seriam necessários
coordenação e armazenamento compartilhados. Auth PBKDF2/HMAC é demonstrativa. CI/Docker configurados não
comprovam execução hospedada. Requisição interrompida fica reservada e exige reconciliação pelo histórico;
isso evita repetição silenciosa, mas não é recuperação automática exatamente-uma-vez.
