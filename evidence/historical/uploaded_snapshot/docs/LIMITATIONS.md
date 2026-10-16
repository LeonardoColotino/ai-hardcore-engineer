# Limites e validações pendentes

Esta entrega é uma evolução verificável da V3, com aprovação parcial. A meta 9,5/10 é pessoal; nenhuma nota ou aprovação oficial é atribuída.

- **Modelo real e fatos:** nenhum Ollama está acessível neste ambiente. Grounding, relevância média ≥1,8/2, respostas úteis ≥90%, seleção ≥95% em avaliação live, três repetições críticas e p95 aquecido ≤60s ainda precisam de captura e revisão factual. O filtro de relevância e as proteções de contratação são heurísticos, não prova de entailment de cada afirmação. `requires_factual_review` permanece pendência.
- **Corpus:** o índice anexado é histórico. Novos metadados/manifesto e limpeza não tornam retroativamente o corpus antigo atualizado. Reconstrua com as URLs oficiais e embeddings Ollama; confira seções e trechos completos. Seed/hash offline exercita mecanismos e não comprova informação comercial oficial.
- **Navegador:** JavaScript teve sintaxe verificada e revisão estática independente. Falha de download do Chromium impediu E2E e inspeção visual 1280×800/390×844. Execute o smoke local e revise imagens. Os screenshots de QA não são entregáveis persistentes.
- **Docker e Windows:** Docker não está instalado; build/run/health/retencão de volume não foram executados. Windows/PowerShell não disponível. Instalação exata das dependências sofreu bloqueio de rede; resultados de testes usam versões efetivamente instaladas registradas em evidências.
- **Memória:** estado de entidades persistido e janela limitada de histórico; resolução de referências usa política lexical e catálogo de entidades reconhecidas. Não é memória semântica geral. Mudanças de assunto, produtos desconhecidos e longos históricos precisam de avaliação live.
- **Segurança demo:** tokens HMAC, PBKDF2 e SQLite; sessionStorage no frontend, sem MFA ou revogação por dispositivo. Guardrails por padrões têm limites contra ataques reformulados. Não usar com dados pessoais reais sem revisão de produção.
- **Concorrência e execução:** um processo recomendado; rate limit, métricas e locks são locais ao processo. Orçamento de rede não garante cancelamento duro de uma resposta que envia bytes continuamente. Não há retry automático do chat: após erro/timeout, atualize histórico antes de reenviar.
- **Handoff:** SQLite mantém estados e resposta humana. O protocolo não significa mensagem enviada a um time externo. Repetições podem reutilizar ticket aberto; não representam idempotência completa de mensagens ou replies.
- **Observabilidade:** métricas locais reiniciam com servidor. Não há monitoramento externo, alerta ou medição confirmada de hardware/GPU/digest do modelo.
- **Validação reservada:** dataset criado pelo QA antes das correções; compartilhamento de workspace não constitui conjunto secreto ou revisão humana. Leia TEST_PLAN.md e INDEPENDENT_REVIEW.md.

Antes de submissão integral, feche os gates de ACCEPTANCE_CRITERIA.md com evidências da mesma versão do código e corpus. Nenhum fallback ou abstention pode ser contado automaticamente como resposta útil.
