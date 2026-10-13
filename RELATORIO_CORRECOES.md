# Correções após avaliação ao vivo — 13/10/2026

O ZIP enviado foi preservado. Esta cópia contém correções e novos testes de regressão; não é aprovação final de qualidade nem garantia de nota.

## Evidências executadas neste ambiente

- Os 15 testes novos falharam na cópia original reconstruída do ZIP. Registro: evidence/baseline-15-regressions.txt.
- Na versão corrigida: 92 testes passaram, com um aviso de depreciação. Registro: evidence/pytest-corrections.txt.
- 17 cenários offline passaram nos contratos de roteamento, ferramentas, presença de fontes e comportamento de falha. evaluation/report.json. Não medem relevância ou veracidade das respostas.
- A captura recebida está preservada em evidence/historical/live-development-before-corrections.json. Ela precede estas alterações e não valida este candidato.

## Alterações

1. Extração HTML preserva descrições DIV/SPAN e remove navegação. Deve-se reconstruir o índice; esta correção foi testada com fixture HTML, sem validar novamente o site real.
2. Recuperação filtra fontes de produtos diferentes antes de gerar a resposta, busca mais candidatos e amplia sinônimos. Uma fonte Pix não comprova biometria da Get Smart.
3. Comparações preservam as duas entidades explícitas; agradecimentos não criam tickets; continuação de depósito reutiliza a conta autenticada e a ferramenta anterior.
4. Ausência de evidência e respostas interrompidas pelo limite do Ollama não são registradas como resolução. Fontes são mantidas quando há encaminhamento.
5. Requisitos de conta do comprador e algumas funcionalidades sensíveis exigem evidência explícita. O filtro é conservador e lexical: não é um verificador universal de fatos.
6. Suporte responde em português. O mesmo prompt breve passa a ser usado na geração a partir de fontes web.
7. Limite de saída configurável por LLM_MAX_OUTPUT_TOKENS, padrão 96. Se a geração terminar por limite, há encaminhamento; aumentá-lo pode elevar a latência.
8. Interface evita aviso de contingência redundante em tickets e preserva novo texto digitado enquanto uma requisição anterior termina.
9. Corpus offline corrige a fonte de demonstração de maquininhas antes indevidamente rotulada como Pix. Continua sendo demonstração, não prova documental atual.

## Pendências antes da entrega

Repetir desenvolvimento e validação com Ollama, revisar factualidade contra fontes completas, avaliar latência e respostas interrompidas. Validar interface em navegador, isolamento entre usuários e fluxo OPEN → IN_PROGRESS → RESOLVED → CLOSED. Testar reconstrução do índice e Docker no Windows.

Ollama, Docker e navegador não foram executados neste ambiente. As validações que você fez anteriormente são evidências do candidato anterior. Não foi realizada revisão independente por outro agente nesta rodada. Os documentos de auditoria antigos no pacote são históricos e não certificam estas alterações.

A limpeza de HTML ainda pode conter publicidade. Relevância de fonte, factualidade e completude precisam de revisão humana. Não atribuí uma nota estimada.
