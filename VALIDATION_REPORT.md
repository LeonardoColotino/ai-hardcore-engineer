# Validação da entrega consolidada

Estado: versão final organizada, com limitações conhecidas; sem garantia de nota ou certificação de produção.

## Procedência das evidências

1. Execução neste ambiente: suíte Python de 248 casos; APIs via TestClient; especialistas/provedores simulados quando declarado. Pacote limpo executado: 248 passed, 1 warning in 8.51s. Execução local não significa Docker/Windows neste ambiente.
2. Execução no notebook do usuário: saída copiada no chat informa 248 passed, 1 warning in 38.45s após revisão 6. Docker iniciado, health ok, Ollama configurado e índice pronto. Não há atestado independente nem hash vinculado a cada captura local.
3. Capturas reais fornecidas pelo usuário: `comparacao-modos-revisao5.json` e captura anterior preservada como histórica. Modelo llama3.2:3b, mesmos registros dentro de cada comparação, 3 perguntas × 2 modos. Não são holdout nem medição estatística.
4. Fluxo manual relatado: capital Argentina, Link de Pagamento com continuação, payment_status demonstrativo, ticket T-131d79c350dc4c59 respondido pelo operador e encerrado. Evidências aqui são transcrições/relatos, não uma gravação do navegador.
5. Artefatos herdados em evidence/historical* e docs/historical-pre-delivery não aprovam automaticamente esta entrega. Este relatório e README prevalecem sobre números ou pendências antigas.

## Comparação real de desenvolvimento

| Caso evidence | Antes (s) | Revisão 5 (s) | Observação |
|---|---:|---:|---|
| Cartão virtual: Conta Digital ou Link | 66,7 | 28,5 | Atribuição correta, sem benefícios extras |
| Mesma pergunta em ordem invertida | 50,9 | 14,9 | Associação mantida |
| Funcionalidades da Conta Digital | 37,2 | 41,5 | Três itens documentados preservados |

No prose da revisão 5, houve abstenção segura nos três casos. Isso mede contenção dos problemas observados, não capacidade de responder corretamente. Não ativar prose com base nesses resultados. Latências têm variação de aquecimento/hardware e amostra pequena; não inferir ganho universal.

## Validação estrutural

Os 17 cenários offline verificam roteamento, ferramentas, presença de fontes/trechos e falhas usando web simulada e geração desabilitada. As métricas históricas de 1,0 não são acurácia factual ou relevância. O relatório atual de execução será colocado em evidence/current/offline-report.json.

## Limites de aprovação

Persistem clareza de catálogo, tutorial para pergunta geral, clarificação de produto indefinido, revisor semântico falível, guards lexicais limitados e possível divergência entre timeout visual e requisição concluída. Não houve novo benchmark amplo de geração, auditoria externa, teste de carga ou execução real dos opcionais GGUF/reranker/OIDC. O vídeo final não foi produzido.

A limpeza de conversas locais foi solicitada para organizar a interface, com backup. Não é evidência de taxa de acerto; resultados com falhas permanecem nos relatórios históricos. Nenhum banco privado deve ser anexado à entrega.

## Atualização — revisão 7, 16/10/2026

Na execução local do autor com Docker, 261 testes passaram, com 1 aviso.
O cenário de conexão percorreu support → knowledge → escalation.
A publicidade deixou de ser apresentada como orientação técnica.
Sem instruções suficientes, foi criado um ticket; a resposta humana
apareceu na conversa e o ticket foi encerrado.

Essa verificação confirma o encaminhamento operacional, não a solução
automática da conexão nem a qualidade de todas as respostas.
Detalhes: evidence/VALIDACAO_LOCAL_REVISAO_7.md.
Os resultados anteriores correspondem às versões indicadas.
