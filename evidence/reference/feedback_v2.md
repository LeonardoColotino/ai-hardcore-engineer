# Feedback — LeonardoColotino

**Repositório:** `LeonardoColotino/ai-hardcore-engineer`  
**Nota anterior:** 7,2/10  
**Nota atual:** **7,7/10**  
**Variação:** **+0,5**  
**Referência:** João / Skywalker = 10,0

## Resumo

A versão atual do repo é materialmente melhor que a primeira avaliada. A v2 adiciona guardrails, agente de escalonamento, routing híbrido LLM + fallback determinístico, RAG com threshold/deduplicação, 46 testes, avaliação offline com 17 casos e observabilidade estruturada.

O principal teto continua sendo a ausência de memória multi-turn, human handoff operacional e colaboração real entre especialistas.

## Critérios

| Critério | Nota |
|---|---:|
| Arquitetura / código | **8,9** |
| Multi-agent / orchestration | **7,3** |
| RAG / Knowledge | **8,6** |
| Segurança / isolamento | **7,2** |
| Testes / quality | **8,8** |
| Observabilidade / evals | **7,8** |
| Memória / multi-turn | **1,0** |
| Human-in-the-loop | **2,5** |
| Infra / Docker | **8,2** |
| Produto / completude | **8,5** |
| Trade-offs / engenharia | **9,5** |
| **Nota final** | **7,7/10** |

## O que melhorou

### Router

O Router tenta classificação estruturada por LLM, valida a resposta e exige confiança mínima. Quando o LLM falha ou está indisponível, usa fallback determinístico.

Ainda assim, escolhe apenas um destino entre `knowledge`, `support` ou `escalation`.

### RAG

A versão atual possui:

- embeddings;
- vector store NumPy persistente;
- cosine search;
- `top_k`;
- `min_score`;
- deduplicação;
- metadata/source;
- fallback web;
- abstention sem evidência suficiente.

A escolha de NumPy em vez de FAISS é justificada pelo tamanho reduzido do corpus.

### Testes e evals

O projeto reporta **46 testes passando** cobrindo routing, tools, isolamento de usuário, RAG, guardrails, API e failure modes.

Existe também um runner de avaliação offline com **17 casos E2E**, medindo routing accuracy, tool selection, presença de sources/excerpts e comportamento de falha/escalation.

### Observabilidade

Agora há logging JSON estruturado com `request_id`, agente, tool, duração, confidence, escalation e routing reason.

## Principais gaps

### Memória multi-turn ausente

O contrato da API recebe apenas `message` e `user_id`; não há `session_id`, histórico ou checkpoint. Cada request continua independente.

### Human handoff ainda simulado

Existe `EscalationAgent`, mas ele apenas recomenda revisão humana. Não há ticket real, fila, operador ou resposta humana retornando à sessão.

### Multi-agent simples

Fluxo atual:

```text
Guardrail
   ↓
Router
   ↓
Knowledge OU Support OU Escalation
```

Se Knowledge/Support falharem, cai para Escalation. Não existe sequência entre especialistas nem supervisor com replanejamento.

### Segurança ainda depende do caller

O `user_id` é recebido pela API e usado nas tools, sem autenticação real do caller. O LLM não escolhe outra identidade, o que é positivo, mas a boundary externa continua incompleta.

### Docker não totalmente validado

Existem Dockerfile e Docker Compose, mas o próprio projeto informa que Docker/Ollama ainda não foram plenamente validados no ambiente do autor.

## Comparação com João

Leonardo evoluiu bastante em fallback determinístico, RAG com abstention, testes offline, evals e observabilidade.

João continua muito superior em memória, colaboração/supervisão agentic, autenticação, autorização, handoff humano operacional e profundidade de observabilidade/evaluation.

## Veredito

**Bom, com evolução clara na v2.**

A nova versão demonstra uma solução mais disciplinada e madura. Ainda não entra no grupo 8,5+ por faltar memória, colaboração real entre agentes, autenticação e human-in-the-loop operacional.

**Nota revisada: 7,7/10.**
