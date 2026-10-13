# Aplicar candidato 1.4

Extraia o ZIP em pasta separada. Abra PowerShell na pasta que contém este documento.

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File ".\scripts\apply_update.ps1" -Target "C:\Users\joaol\Desktop\Codigos\ai-hardcore-engineer-v3-evoluido\ai-hardcore-engineer-v3-evoluido1.0"
```

O script cria backup. Preserva .env, banco, identidades e volumes. Não é necessário reconstruir o índice: esta alteração é do cliente e da seleção. Mantenha o mesmo nome de projeto Compose, sem down -v.

Execute um comando por vez e pare se houver erro:

```powershell
cd "C:\Users\joaol\Desktop\Codigos\ai-hardcore-engineer-v3-evoluido\ai-hardcore-engineer-v3-evoluido1.0"
docker compose -p ai-hardcore-engineer-v3-evoluido up -d --build --force-recreate
docker compose -p ai-hardcore-engineer-v3-evoluido exec api python -m pytest -q -p no:cacheprovider
docker compose -p ai-hardcore-engineer-v3-evoluido exec api python -m evaluation.run --output /state/offline_report_final.json
Invoke-RestMethod -Uri "http://127.0.0.1:8000/health"
```

Esperado: 149 testes, 17 casos offline e saúde ok/ollama/True. Não constitui aprovação factual.

Capture development com Ollama aberto, sem consultas simultâneas:

```powershell
docker compose -p ai-hardcore-engineer-v3-evoluido exec api python -m evaluation.live --dataset development --repetitions 1 --timeout 300 --output /state/live_development_final.json
docker compose -p ai-hardcore-engineer-v3-evoluido cp api:/state/live_development_final.json .\live_development_final.json
```

Envie o JSON para revisão. Depois de confirmar a captura, execute perguntas distintas de validation:

```powershell
docker compose -p ai-hardcore-engineer-v3-evoluido exec api python -m evaluation.live --dataset validation --repetitions 1 --timeout 300 --output /state/live_validation_final.json
docker compose -p ai-hardcore-engineer-v3-evoluido cp api:/state/live_validation_final.json .\live_validation_final.json
```

Envie também esse JSON. Não ajuste o sistema apenas para passar nesses exemplos; se houver falha, documente e teste a correção com casos novos. Uma repetição é triagem; use três para avaliar estabilidade do candidato aprovado. Não envie .env ou credenciais.
