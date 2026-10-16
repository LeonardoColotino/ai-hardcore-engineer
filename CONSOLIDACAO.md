> Documento de arquitetura/base herdado. Revisões 1–6 estão consolidadas; para resultados e limitações atuais, consulte README.md e VALIDATION_REPORT.md.

# Consolidação — origens e decisões

## Preservado da V4-final

Plano tipado com dependências e falhas por tarefa, composição de respostas parciais, diagnóstico público sanitizado, transações/idempotência de tickets/respostas e reservas HTTP, pausa de automação durante handoff, traces/feedback protegidos, ingestão com validação de host/redirect/DNS/tamanho, manifesto íntegro do índice e CI/smokes.

## Recuperado da V4-COMPLETO e V3 1.4

Clientes opcionais GGUF e OpenAI-compatible, Ollama structured output, OIDC RS256 com vínculo de papel server-side, BM25/RRF e cross-encoder opcional, seleção validada de evidências, extração de procedimentos/condições comerciais/Pix, 14 snapshots oficiais, dataset histórico de retrieval e vídeo antigo identificado. Regressões `second`, `third`, `fourth` e `final_selection` foram recuperadas do snapshot V3 disponível neste workspace, com a fixture JSON correspondente.

Não se substituiu o supervisor final pelo antigo: foi recuperada revisão estruturada de cobertura pública dentro do executor de tarefas. Tokens foram ligados ao contexto de telemetria final. Provedores opcionais também podem planejar. Schema JSON e truncamento permanecem identificados; nenhuma integração concede acesso a outro usuário.

## Adaptações de contrato

Duas fixtures de HTML antigas agora simulam DNS público, status, cabeçalhos e streaming de bytes exigidos pelo fetch protegido. Asserções sobre seções e conteúdo foram mantidas. O teste de geração numérica livre passou a declarar `answer_mode=prose`; o modo de seleção é testado pelas regressões recuperadas. Fixture de clima/cotação estrutural agora tem valores e data expressamente fictícios para exercitar controles de atualidade sem enfraquecê-los. Dataset original não foi alterado.

## Novos controles e correções

IDs de fonte não são reindexados após remoção silenciosa de blocos: contexto inseguro ou acima do orçamento causa abstention. Extração HTML mantém heading com seu conteúdo aninhado. RRF preserva cosseno dos candidatos lexicais fora do top-k denso. Revisão de conflito/falha abstém aquela tarefa sem apagar outras. GGUF mantém erro específico de truncamento e valida conteúdo. Provedor desconhecido falha explicitamente. Readiness distingue perfis e não afirma inferência.

## Limites

Não há novo parecer delegado independente desta consolidação: a implementação e verificação foram feitas pelo mesmo agente. Relatórios de QA/Validator dos inputs estão em histórico. Métricas antigas não são transferidas como aprovação do release novo. Novos testes verificam contratos com provedores/reranker simulados e assinatura RSA local real; inferência, IdP externo, Docker e navegador ainda exigem execução apropriada.
