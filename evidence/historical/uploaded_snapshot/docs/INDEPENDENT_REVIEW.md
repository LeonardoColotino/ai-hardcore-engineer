# Parecer independente do candidato

**Decisão: aceitar a evolução determinística no escopo demonstrativo; rejeitar aprovação integral para submissão pelos critérios do prompt.** Revisão de um agente de IA separado da implementação e do QA, não avaliação humana nem nota oficial. Data: 2026-10-12 UTC. O desafio original permanece fonte dos requisitos obrigatórios.

## Evidência e versão

O validador leu o master, desafio, feedback e captura live histórica; inspecionou código de produção, corpus completo dos chunks Link de Pagamento, estados persistidos, resultados brutos e frontend. Não tomou testes verdes como prova de qualidade semântica.

Após congelamento, executou `python -m pytest -q`: **77 passaram, 1 warning, 5,19 s**, no Linux/Python 3.12.14 disponível. `evidence/independent-manifest.json` registra versões, arquivos e digest de código/datasets revisados. Instalação exata dos pins não foi conseguida; FastAPI disponível 0.143.0 difere do pin 0.142.4. Warning TestClient/httpx permanece. QA executou separadamente a mesma suíte (`evidence/qa-final.txt`, 5,14 s) e avaliação offline (`evidence/offline-final.txt`, 17 cenários estruturais). Essas métricas não são grounding semântico.

Uma execução adicional, independente dos asserts do QA, enviou pedido de humano pela API com banco temporário e inspecionou SQLite diretamente. `evidence/independent-probe.json` contém resposta bruta, ticket e histórico: protocolo da resposta corresponde ao registro do cliente autenticado; OPEN → IN_PROGRESS → RESOLVED → CLOSED retornou 200; registro final CLOSED mantém operador e resposta; mensagem humana consta no histórico. Acesso de outro cliente a ticket/sessão retornou 404 e ação de operador por cliente retornou 403. Sem índice, readiness retornou 503. Não foram usadas credenciais ou dados reais.

## Achados corrigidos e revisão factual

O baseline tinha referências por regex exata e catálogo fabricado, seleção indevida de Support para contratação, mensagens de ticket recomendado apesar da persistência, ferramentas atribuídas à etapa errada, metadados de geração perdidos na colaboração e reset de tracing sem finally. Regressões e código final mostram política de intenção, estado persistido por dono, candidatos extraídos da resposta, metadados preservados, criação confirmada após commit e finally.

O validador encontrou uma falha adicional na nova proteção: a expressão “produtos e serviços contratados” fazia `signup_evidence` retornar True sem procedimento de contratação. Reportou ao implementador/QA. Após correção, a mesma entrada retorna False; regressões cobrem disclaimer e CTA. Isso corrige o falso positivo reproduzido, mas a proteção continua lexical. Não constitui entailment nem verifica cada taxa/condição/requisito gerado.

Inspeção dos chunks históricos do Link confirma RNE, carrinho e frete presentes. São dados reais no arquivo histórico, não erros a remover arbitrariamente. O trecho sobre Portal Minha Conta explica criação/uso do link, sem comprovar adesão. Há chunks começando em “ocê” e “es disponíveis”, conteúdo de interface e taxa histórica; o código novo de chunking não corrige retroativamente o índice anexado. O corpus legado contém 20 chunks, marcador `ollama`, sem manifesto/datas/modelo verificável. Deve ser reconstruído e avaliado antes de usar como evidência atual. Nenhuma consulta externa foi tomada como confirmação de preço vigente.

## Frontend

Revisão estática encontrou e encaminhou riscos de estado: sidebar de cliente após troca de papel, resposta antiga de tickets sobrescrevendo atualização e resposta de chat anterior retornando após logout. Correções inspecionadas incluem limpeza de sidebar/signatures, contador de resposta de tickets, epoch por sessão/envio e token capturado por request. Markdown utiliza nós de texto/strong/listas; links aceitam somente http/https; conteúdo e resposta humana não entram via HTML bruto. Backend exige papel de operador, e UI esconde ações ao cliente. Não foi encontrado vetor direto de HTML/script XSS nesse caminho revisado.

**Aprovação visual e E2E pendentes:** sintaxe e inspeção não verificam layout, foco, contraste, Enter, mobile, polling, expiração ou concorrência real no navegador. Chromium ausente e download truncado impediram execução. Execute `scripts/browser_smoke.cjs` e inspecione desktop 1280×800/mobile 390×844.

## Gates que impedem aprovação integral

| Gate | Estado e fundamento |
|---|---|
| Obrigatórios estruturais | Três agentes + Escalation, tools Support, API, RAG/web, Docker e README presentes; integração real RAG/LLM/container não confirmada |
| Segurança/handoff/memória determinística | Testes passaram e probe confirmou ticket/isolamento; política lexical de referentes ainda limitada |
| Zero afirmação crítica sem fonte aplicável | **Não verificado** com geração real; `requires_factual_review` não é aprovação factual |
| ≥90% resposta útil, ≥95% routing/tools live, qualidade ≥1,8/2 | **Pendentes**; sem captura da versão final com Ollama e corpus reingerido |
| Três repetições dos fluxos críticos | Dataset/runner preparados, execução real pendente |
| p95 aquecido ≤60 s | Métricas e orçamento implementados, hardware/modelo/latência real não medidos |
| Docker, Windows, instalação limpa | Pendentes: runtime Docker/Windows ausentes, instalação pins bloqueada |
| Browser comportamento/visual | Pendente: nenhum navegador executado |
| Repository e vídeo | Preparação entregue; publicação/submissão não realizadas nem autorizadas |

Não restou falha determinística reproduzida e não corrigida nos casos executados após freeze. Isso não demonstra inexistência de defeitos fora desse conjunto. Permanecem limitações confirmadas de escopo: relevância/abstention/signup lexicais; embedding-modelo não identificado integralmente no legado; orçamento limita chamadas e inatividade de rede, não cancela duramente fluxo que envia bytes; locks/métricas locais de processo; sem idempotência completa do chat; corpus histórico não reconstruído.

`answered`/`resolved` em metadata são outcomes técnicos, não certificação de resolução factual. `/metrics` mantém qualidade grounded como null e explicação. `quality_grounded_rate` não deve ser preenchida com presença de excerpt.

## Próximo aceite

Reconstruir corpus oficial, executar datasets desenvolvimento20/validação10 com três repetições críticas, revisar respostas contra trechos completos, pontuar casos e denominadores, medir warm/cold p50/p95, executar Windows/container/restart/persistência e browser. O conjunto reservado foi definido pelo QA mas o workspace é compartilhado; não há alegação de holdout secreto. Mudança de produção exige rerun, nova revisão e reconstrução do ZIP. Até fechar esses gates, a entrega continua **parcial e pendente**, independentemente de testes verdes.
