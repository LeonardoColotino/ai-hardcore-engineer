# Aplicar no seu projeto atual

1. Extraia este ZIP em uma pasta separada. Preserve seu projeto atual e o arquivo .env.
2. Abra PowerShell na pasta extraída que contém este documento e execute:

```powershell
.\scripts\apply_to_existing.ps1 -Target "C:\Users\joaol\Desktop\Codigos\ai-hardcore-engineer-v3-evoluido\ai-hardcore-engineer-v3-evoluido"
```

O script copia somente arquivos alterados e cria backup deles. Não copia .env, banco, identidades nem índice. Não exclua volumes e não use docker compose down -v.

3. Entre na pasta ORIGINAL e reconstrua a imagem:

```powershell
cd "C:\Users\joaol\Desktop\Codigos\ai-hardcore-engineer-v3-evoluido\ai-hardcore-engineer-v3-evoluido"
docker compose build
docker compose run --rm api python -m app.rag.ingest --ollama-embeddings
docker compose up -d --force-recreate
docker compose exec api python -m pytest -q
docker compose exec api python -m evaluation.run
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```

Reconstruir o índice é necessário para recuperar as descrições antes descartadas. Mantenha o mesmo diretório e nome de projeto Compose para reutilizar seu volume. Não precisa criar venv para usar Docker. .env.example é apenas modelo e não contém segredos; não substitui sua configuração atual.

4. Com Ollama e aplicação ativos, capture novamente:

```powershell
docker compose exec api python -m evaluation.live --dataset development --repetitions 1 --timeout 300 --output /state/live_development_after_corrections.json
docker compose cp api:/state/live_development_after_corrections.json .\live_development_after_corrections.json
```

Revise respostas e fontes completas. Depois execute o conjunto validation sem ajustar o código para suas respostas:

```powershell
docker compose exec api python -m evaluation.live --dataset validation --repetitions 1 --timeout 300 --output /state/live_validation_after_corrections.json
docker compose cp api:/state/live_validation_after_corrections.json .\live_validation_after_corrections.json
```

Uma repetição é triagem; use três para medir estabilidade após corrigir problemas. Envie os dois JSONs e logs de falha para revisão. HTTP 200 e testes offline não comprovam factualidade. Não envie .env, banco ou credenciais.
