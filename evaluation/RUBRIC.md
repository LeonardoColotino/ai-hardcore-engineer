# Protocolo de avaliação factual — v2 QA

Três conjuntos versionados UTF-8: histórico L1–L8 `live_dataset.json`; desenvolvimento D01–D20; validação V01–V10. Desenvolvimento+validação incluem 14 sequências multi-turn. Validação foi produzida separadamente por QA antes de correções, mas arquivos são acessíveis a todos; não alegar holdout oculto nem independência se utilizados para ajustar código.

Com API autenticada, índice real e LLM_PROVIDER=ollama execute:

```
python -m evaluation.live --dataset development --repetitions 3
python -m evaluation.live --dataset validation --repetitions 3
```

Não foi executado Ollama aqui. Runner captura respostas HTTP e erros com versão SHA do app/dataset e tempos, checkpoints por cenário, sem tokens. Anexar também configuração efetiva do servidor (sem secret), modelo/digest (`ollama list` e `ollama show llama3.2:3b`), corpus/provider/hash, CPU/RAM/GPU observada, cold/warm start e data. `health.llm_provider` não prova acessibilidade, modelo carregado nem GPU. Hash local do app só vincula servidor se este roda o mesmo checkout: registrar essa correlação.

## Revisão por cenário

Identificar reviewer_type (`human` ou `AI_agent`), identidade/data e justificativa por nota. Nenhuma nota automática. Abrir trechos completos, não somente URL/score/snippet. Dimensões aplicáveis: intenção/roteamento, tool autorizada, relevância/produto, groundedness de cada afirmação crítica, continuidade, colaboração, abstention/handoff e utilidade. Rubrica: 0 incorreto, 1 parcial, 2 atende. N/A só com justificativa e fora do denominador daquela dimensão. Não chamar julgamento IA de humano.

Separar pergunta contratual de criação de link; conferir taxas, elegibilidade, prazos e necessidade de conta comprador no produto correspondente. Documento com CTA ou disclaimer não é procedimento. Fontes irrelevantes não suportam resposta. Resposta sem informação/técnica não conta como resolução. Fallback extrativo não é geração e não recebe aprovação semântica automática.

## Denominadores e critérios fixos

- Todas tentativas e falhas são mantidas, inclusive turnos bloqueados após erro de continuidade. Publicar resultado de cada repetição crítica.
- Roteamento e tool ≥95%, zero ferramentas de conta em produto/contratação.
- Utilidade fundamentada ≥90% dos casos com evidência suficiente; abstenção/fallback não são úteis só por serem seguros.
- Groundedness e relevância médias ≥1.8/2, nenhuma dimensão crítica zero. Zero afirmação crítica sem apoio.
- Memória/identidade/handoff críticos devem passar em todas repetições.
- Erros, fallback, abstention, handoff e sucesso técnico têm contagem e denominador explícitos. HTTP200 não comprova resolução.
- Latência warm serial p95≤60s, medida com todos outliers; não extrapolar de fixture offline. Publicar hardware, amostra e p50/p95.

A captura ainda precisa de revisão factual e cálculo dessas métricas. Um relatório com `quality_status=pending_factual_review` não aprova critérios. Presença de excerpt é proxy estrutural separado, nunca groundedness.
