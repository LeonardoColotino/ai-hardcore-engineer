# Checklist de submissão

- [ ] Ler VALIDATION_REPORT.md e INDEPENDENT_REVIEW.md; fechar rejeições e pendências críticas.
- [ ] Windows: recriar venv, instalar requisitos exatos, provisionar demo e rodar scripts/validate_windows.ps1.
- [ ] Ollama: confirmar modelos existentes, reconstruir corpus real, iniciar API com provider ollama.
- [ ] Capturar desenvolvimento e validação com três repetições; revisar respostas contra trechos completos e registrar avaliador/rubrica.
- [ ] Não chamar métricas offline de grounding; medir utilidade, falhas e p50/p95 com denominadores.
- [ ] Executar scripts/browser_smoke.cjs com API e revisar desktop/mobile, operador e cliente.
- [ ] Docker: build, provisionar, health/readiness, chat, operador, reinício e volume preservado.
- [ ] Conferir .env.example; excluir .env, usuários provisionados, bancos pessoais, venv e caches do GitHub.
- [ ] Gravar vídeo de 5–7 minutos usando DEMO_SCRIPT.md e resultados verdadeiros.
- [ ] Publicar GitHub e vídeo por ação explícita do proprietário; nenhuma publicação foi feita nesta entrega.

## Captura local (API com Ollama ativa)

```powershell
.\.venv\Scripts\python.exe -m evaluation.live --dataset development --repetitions 3
.\.venv\Scripts\python.exe -m evaluation.live --dataset validation --repetitions 3
```

Forneça DEMO_PASSWORD por ambiente local ou prompt oculto; não compartilhe senhas/.env. O runner captura erros e fallbacks; qualidade permanece pendente até revisão factual, inclusive dos casos difíceis.
