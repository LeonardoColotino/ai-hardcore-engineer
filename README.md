# Getnet — assistente multiagente V4, revisões 1–6

API HTTP com interface de chat e operador. Router/Planner coordena Knowledge (RAG e busca web), Support (consulta autenticada de cliente, pagamentos, transações e diagnóstico demonstrativo) e Escalation. SQLite mantém sessões, contexto por proprietário, tickets, respostas humanas, idempotência e traces. **Dados de suporte são fictícios; não há conexão com transações financeiras reais.**

## O que esta entrega comprova

- 248 testes automatizados no candidato local; o usuário também executou 248 testes no Docker/Windows (saída informada, 38,45 s).
- Duas capturas reais com Ollama `llama3.2:3b`, preservadas para comparação. Na revisão 5, o modo evidence atribuiu cartão virtual à Conta Digital sem benefícios extras nas duas formulações testadas e preservou os três benefícios documentados da conta. Prose permaneceu insuficiente; as respostas problemáticas foram contidas. Esta é uma amostra de desenvolvimento de 3 perguntas em 2 modos, não uma certificação geral.
- Usuário confirmou no navegador: procedimento com continuação "esse link", busca web da capital da Argentina, consulta demonstrativa do último pagamento e handoff com resposta do operador visível ao cliente e ticket encerrado. São relatos da execução local, não uma gravação independente.
- Testes estruturais offline usam especialistas/web simulados. **Fonte presente e trecho citado não significam relevância, completude ou veracidade.**

Consulte [VALIDATION_REPORT.md](VALIDATION_REPORT.md), [LIMITATIONS.md](LIMITATIONS.md) e `evidence/current/`. Evidência anterior está identificada como histórica. O vídeo final não foi gravado nesta entrega; há roteiro em [ROTEIRO_VIDEO.md](ROTEIRO_VIDEO.md).

## Leitura e testes sem Ollama

Não é preciso ter Ollama para analisar o código ou executar os testes offline. Requer Python 3.12; ambiente virtual é recomendado fora do Docker.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m pytest tests -q -p no:cacheprovider
.\.venv\Scripts\python.exe -m evaluation.run --output evidence/current/offline-report.json
```

A suíte usa dados temporários e simulações declaradas. Não exige uma chave de API, pesos ou servidor de modelo. A avaliação estruturada possui 17 cenários e não é uma nota de qualidade factual.

## Docker: instalação nova

Docker Desktop iniciado. Não precisa de venv no host. Não reutilize banco/credenciais pessoais para uma instalação de avaliação.

```powershell
Copy-Item .env.example .env
notepad .env
```

Preencha `AUTH_SECRET` (pelo menos 32 caracteres aleatórios) e `DEMO_PASSWORD` (pelo menos 10 caracteres, escolhida localmente). Mantenha `.env` fora do Git/ZIP. Para gerar um segredo pelo PowerShell:

```powershell
[guid]::NewGuid().ToString('N') + [guid]::NewGuid().ToString('N')
```

Perfil inicial `.env.example`: `LLM_PROVIDER=disabled`, `KNOWLEDGE_ANSWER_MODE=evidence`. Isso permite testar ferramentas, API e contingência, **sem geração real**. Para reconstruir um índice sem internet, use os snapshots oficiais herdados; são históricos, não garantem tarifas atuais.

```powershell
docker compose -p getnet-v4-consolidado build
docker compose -p getnet-v4-consolidado run --rm api python scripts/init_demo.py
docker compose -p getnet-v4-consolidado run --rm api python -m scripts.rebuild_snapshot_index
docker compose -p getnet-v4-consolidado up -d
Invoke-RestMethod -Uri http://127.0.0.1:8000/health
```

Abra http://127.0.0.1:8000. Clientes `cliente1988` e `cliente2026`; operador `operador`. Senha: a que você escolheu no `.env`. Para o operador, use outra janela/perfil de navegador. Se a porta 8000 estiver ocupada, identifique a instância anterior; não apague volumes para liberar a porta.

```powershell
docker compose -p getnet-v4-consolidado exec api python -m pytest tests -q -p no:cacheprovider
docker compose -p getnet-v4-consolidado exec api python -m evaluation.run --output /state/offline-report.json
```

Para a instalação já validada pelo usuário, o código das seis revisões está consolidado aqui. Não é necessário reaplicar patches, reinstalar modelos, limpar banco ou reconstruir índice se o provedor de embeddings não mudar. Os comandos de provisionamento acima são para instalação nova.

## Ollama real, opcional para testes de geração

No host, disponha dos modelos `llama3.2:3b` e `nomic-embed-text:latest`. Configure no `.env`:

```dotenv
LLM_PROVIDER=ollama
OLLAMA_CHAT_MODEL=llama3.2:3b
OLLAMA_EMBED_MODEL=nomic-embed-text:latest
KNOWLEDGE_ANSWER_MODE=evidence
REQUEST_TIMEOUT_S=120
CHAT_BUDGET_S=300
```

Compose usa `host.docker.internal:11434` para alcançar o Ollama do host. Fora do Docker, o padrão é localhost. Indexação real requer internet e Ollama acessível:

```powershell
docker compose -p getnet-v4-consolidado run --rm api python -m app.rag.ingest --ollama-embeddings
docker compose -p getnet-v4-consolidado up -d --force-recreate
```

O usuário processou 14 fontes e construiu 123 trechos durante a validação local. Isso não implica que toda página manterá o mesmo conteúdo ou disponibilidade. Reingira ao trocar provedor/modelo de embeddings; não misture índice hashing e modelo neural.

`/health` informa configuração, release e hashes; `inference_verified=false` não é uma medição de geração. `/ready` verifica dependências conforme o perfil, sem provar acerto factual.

## Roteiro básico de demonstração

- Nova conversa: "Como funciona o Link de Pagamento da Getnet?"; continuação: "Como faço para criar esse link?".
- Outra conversa: "Qual é a capital da Argentina?" (busca web com rede disponível).
- Outra conversa: "Qual o status do meu último pagamento?" (registro fixo da identidade autenticada).
- "Quero atendimento humano"; operador assume, responde e encerra. A resposta humana deve aparecer no histórico do cliente.

O exemplo de consulta sobre soluções foi parcialmente informativo; não é apresentado como catálogo completo aprovado. O procedimento ainda é apresentado como tutorial mesmo para "como funciona". Perguntas ambíguas sobre "um produto" não têm clarificação genérica suficiente. Não extrapole o roteiro para alegar aprovação universal.

## Arquitetura e controles

- Planejamento tipado com até 4 tarefas e dependências para diagnóstico Support→Knowledge. Tem fallback determinístico e recuperação oficial limitada; não é autonomia irrestrita.
- Contexto de produto por sessão/proprietário; contexto anexado não é contado como tarefa nova. O histórico não concede identidade ou permissões.
- Source records conservam texto/produto/seção/URL/ID. Seleção usa IDs de candidatos, preserva associações entre fontes e registra escopos ambíguos. Há verificação restrita de citações procedurais e de associações documentais; não constitui entailment universal.
- `evidence` é o perfil recomendado neste candidato. `prose` é experimental; o modelo local gerou erros reais na captura. Abstenções não expõem o parágrafo não validado; uma guarda limitada detecta a confusão observada entre rótulo e outro benefício.
- Recuperação híbrida BM25 + cosseno por RRF, manifesto de integridade do índice, filtros de produto e proveniência. Reranker neural e outros provedores são opcionais, sem aprovação real neste candidato.
- Autenticação demo, escopo de dono no servidor, validação de payload, guardrails, limite de requisições, orçamento de rede e logs. Privacidade e segurança não são certificadas para produção.

[ARCHITECTURE.md](ARCHITECTURE.md) detalha os componentes. `requirements-local.txt` (GGUF), `requirements-semantic.txt` (reranker) e perfis OIDC/OpenAI-compatible são opcionais; não são necessários no roteiro validado, nem exigem API comercial por padrão. Pesos e credenciais não acompanham o ZIP.

## Captura real de comparação

Após configurar Ollama, o script consulta as mesmas fontes recuperadas para os dois modos e salva após cada etapa. Pode demorar minutos. Não modifica `.env` nem conversas de clientes, não atribui nota automática e não valida o supervisor HTTP multi-turn completo.

```powershell
docker compose -p getnet-v4-consolidado exec api python -m scripts.compare_answer_modes --output /state/comparacao-modos.json
docker compose -p getnet-v4-consolidado cp api:/state/comparacao-modos.json .\comparacao-modos.json
```

Preserve resultados anteriores como desenvolvimento. Dados de usuário, senhas, bancos e históricos privados não fazem parte desta distribuição.
