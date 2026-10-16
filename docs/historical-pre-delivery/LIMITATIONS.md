# Limitações do candidato consolidado

- Não há garantia de nota nem certificação de produção.
- Nenhuma inferência real nova desta consolidação. Capturas antigas em histórico não aprovam o candidato atual.
- Docker/CI hospedada não executados aqui. Playwright está instalado, mas faltou binário de navegador. Ollama não está acessível em localhost.
- CrossEncoder/GGUF são opcionais e têm testes de contrato simulados; instalação dos pesos/wheels ainda precisa ser validada no ambiente escolhido.
- Seleção literal verifica origem do trecho, não verdade, pertinência, idioma perfeito, ordenação ou completude. Revisão LLM não equivale a auditoria humana.
- Taxas e condições do snapshot refletem coleta herdada, não atualidade. Corpus reconstruído tem IDs/chunks diferentes dos anteriores; métricas por página não equivalem às antigas métricas de chunk.
- Plano e recuperação têm limites; fallback de intenção ainda usa regras. Paráfrases inéditas precisam de testes live. Sem loops ilimitados ou planejamento livre irrestrito.
- SQLite, locks, rate limit e métricas são single-process. Cancelar espera não interrompe imediatamente inferência síncrona. Não há SLA distribuído.
- DNS é pré-validado, não pinado na conexão; controles de injection/PII não são universais.
- OIDC foi testado com assinatura RSA local e JWKS simulado, não com IdP corporativo. Provisionamento/revogação/segredos corporativos permanecem externos.
- Suporte contém dados demonstrativos fixos, não integra banco real. Sem escritas financeiras.
- Modos de resposta e perfis alteram qualidade/latência: é preciso comparar no mesmo corpus e modelo antes de escolher.
