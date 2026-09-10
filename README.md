# AI Hardcore Engineer

Sistema multiagente desenvolvido em Python para um desafio técnico.

A aplicação utiliza agentes especializados para direcionar perguntas de usuários, consultar informações da Getnet através de RAG, realizar buscas gerais na web e atender solicitações relacionadas a dados de clientes.

## Arquitetura

O sistema possui três agentes principais:

### Router Agent

Responsável por receber a mensagem do usuário e decidir qual agente deve processar a solicitação.

Rotas disponíveis:

- `knowledge`
- `support`

### Knowledge Agent

Responsável por perguntas de conhecimento.

Utiliza duas estratégias:

- **RAG + FAISS** para perguntas relacionadas à Getnet.
- **Web Search** para perguntas gerais.

O conteúdo da Getnet é processado pelo pipeline:

```text
Site Getnet
    ↓
Ingestão
    ↓
Chunks
    ↓
Embeddings
    ↓
FAISS
    ↓
Retriever
    ↓
Knowledge Agent
    ↓
Ollama
```

### Support Agent

Responsável por solicitações relacionadas ao cliente.

Utiliza duas ferramentas:

- consulta de dados do cliente;
- consulta de pagamentos.

Os dados utilizados no projeto são simulados e armazenados em SQLite.

## Fluxo

```text
Usuário
   ↓
FastAPI
   ↓
Router Agent
   ↓
 ┌───────────────┐
 │               │
Knowledge      Support
 Agent          Agent
 │               │
 ├─ RAG          ├─ Customer Database
 │               │
 └─ Web Search   └─ Payment Tool
        ↓
      Ollama
        ↓
     Resposta
```

## Tecnologias

- Python
- FastAPI
- Ollama
- Llama 3.2
- Nomic Embed Text
- FAISS
- SQLite
- DDGS
- BeautifulSoup
- Pytest

## Requisitos

- Python 3.12+
- Ollama

Modelos utilizados:

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

## Instalação

Crie o ambiente virtual:

```bash
python -m venv .venv
```

No Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Instale as dependências:

```bash
python -m pip install -r requirements.txt
```

## Preparando o RAG

Antes de iniciar a aplicação pela primeira vez, execute:

```bash
python -m app.rag.ingest
```

Esse processo coleta o conteúdo utilizado da Getnet, gera embeddings e cria o índice FAISS.

## Executando a aplicação

Execute:

```bash
python -m uvicorn app.main:app --reload
```

A documentação Swagger estará disponível em:

```text
http://127.0.0.1:8000/docs
```

## Exemplo

Endpoint:

```text
POST /chat
```

Request:

```json
{
  "message": "Quais produtos a Getnet oferece?",
  "user_id": "cliente1988"
}
```

Outro exemplo:

```json
{
  "message": "Quando vou receber o dinheiro da minha venda?",
  "user_id": "cliente1988"
}
```

## Testes

Execute:

```bash
python -m pytest -v
```

Os testes cobrem:

- health check da API;
- endpoint `/chat`;
- roteamento para Knowledge Agent;
- roteamento para Support Agent.

## Docker

O projeto inclui um `Dockerfile` como opção de containerização.

O Dockerfile não foi executado durante o desenvolvimento local. A aplicação foi validada diretamente em ambiente Python com Ollama executando localmente.

## Decisões técnicas

O projeto foi mantido propositalmente simples para demonstrar os principais conceitos do desafio sem adicionar complexidade desnecessária.

O Ollama foi utilizado para permitir execução local dos modelos sem dependência de APIs pagas.

FAISS foi utilizado como banco vetorial para o RAG e SQLite para simular os dados necessários ao atendimento do cliente.

A busca web é utilizada pelo Knowledge Agent para perguntas gerais que não dependem da base de conhecimento da Getnet.