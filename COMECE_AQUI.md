# Projeto revisado: próximos passos

Extraia este ZIP em uma pasta nova. Pare o servidor antigo com Ctrl+C.
Não copie a `.venv` antiga. Se tiver um `.env` próprio, preserve uma cópia antes de trocar arquivos.

## 1. Instalar e preparar sem Ollama

No PowerShell, dentro da pasta do projeto:

```powershell
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m app.rag.ingest --seed
python -m pytest -q
python -m evaluation.run
python -m uvicorn app.main:app --reload
```

O seed é um conjunto pequeno de textos de demonstração, com URLs de referência.
Não é uma coleta atual do site Getnet. Os clientes e pagamentos também são fictícios.

## 2. Testar no Swagger

Abra http://127.0.0.1:8000/docs e use `POST /chat`.

Suporte:

```json
{"message":"Quando minhas vendas serão depositadas?","user_id":"cliente1988"}
```

Esperado: `agent=support`, `tool=payment_status`, `escalated=false`.
Os clientes de demonstração são `cliente1988` e `cliente2026`.

RAG offline (a pergunta em inglês facilita a correspondência com o seed em inglês):

```json
{"message":"Getnet payment link WhatsApp","user_id":"cliente1988"}
```

Esperado: `agent=knowledge`, `tool=rag_search`, fontes retornadas.
Hashing offline não entende sinônimos/traduções como embeddings semânticos.

Cliente desconhecido:

```json
{"message":"Quando minhas vendas serão depositadas?","user_id":"unknown"}
```

Esperado: encaminhamento, `previous_agent=support`, `previous_tool=customer_lookup`,
`handoff_reason=customer_not_verified`. Nenhum ticket é criado ou enviado.

Se encaminhar outra pergunta, envie a mensagem, o `user_id` e o JSON completo.
`HTTP 200` confirma processamento; `escalated` e os metadados mostram o resultado.
Os logs antigos enviados não permitem provar a causa exata dos seus três encaminhamentos.

## 3. Conectar Ollama depois

Com Ollama instalado e em execução, pare a API e execute:

```powershell
.\scripts\connect_ollama_windows.ps1
.\scripts\validate_windows.ps1
.\scripts\run_windows.ps1
```

A conexão baixa os modelos, ativa Ollama no `.env` e tenta ingerir o site com embeddings Ollama.
Se a coleta falhar, o script para; resolva a falha antes de declarar a validação concluída.
Os scripts foram revisados, mas não executados no Windows neste ambiente.

## Limites da entrega

46 testes passaram e 17 cenários offline passaram nesta revisão. Há um aviso de depreciação
no TestClient das dependências atuais; ele não causou falha.
Os resultados não medem qualidade factual do LLM nem consultas reais na internet.
Ollama, web real e Docker precisam de validação externa. O índice usa NumPy, não FAISS.
Não há autenticação; não use dados reais nem exponha este protótipo publicamente sem implementá-la.
GitHub e gravação do vídeo permanecem etapas de submissão.
