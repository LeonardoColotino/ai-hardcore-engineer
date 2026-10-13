# Validação da V3 evoluída

**Resultado: aprovação parcial; não pronta para submissão integral pelos gates do prompt.** Nenhuma nota oficial atribuída. Revisão independente realizada por agente de IA, não por avaliador humano.

## Execuções desta entrega

Ambiente Linux, Python 3.12.14. Versões instaladas e hash do código em `evidence/qa-final-manifest.json`. Instalação integral dos pins foi bloqueada por erro de rede403; FastAPI efetivo0.143.0 difere do pin0.142.4. Assim, não afirmamos instalação limpa reproduzível aprovada.

| Verificação | Comando/evidência | Resultado |
|---|---|---|
| Baseline + novas regressões antes de correção | `python -m pytest -q`; qa-baseline.txt | 64 existentes passaram; 7 novas falharam |
| Candidato final QA | `python -m pytest -q`; qa-final.txt | 77 passaram,1 warning,5.14s |
| Avaliação offline | `python -m evaluation.run`; offline-final.txt | 17 cenários; métricas estruturais1.0 |
| Sintaxe frontend | Compilação JS inline e `node --check scripts/browser_smoke.cjs` | passou; não prova layout/interação |
| Revisão independente | INDEPENDENT_REVIEW.md | ver parecer e limitações |
| Ollama real / corpus web atual / semântica / p95 | ui-environment.txt | pendente, servidor indisponível |
| Browser E2E desktop/mobile | ui-environment.txt | pendente, Chromium ausente e download inválido |
| Docker build/run/volume | ui-environment.txt | pendente, executável ausente |
| Windows + instalação exata | dependency-install.txt | pendente, ambiente Windows indisponível e rede bloqueada |

O aviso Starlette/TestClient sobre httpx permanece; nenhuma dependência foi adicionada só para ocultá-lo. Mocks e seed demonstram contratos, persistência e seleção de ferramentas; não representam geração real. HTTP200 e excerpts não significam factualidade ou resolução correta.

## Correções e limites de evidência

Roteamento por intenção antes do classificador, contexto de produto persistido, memória de referências/correções, tickets coerentes após commit, estado humano transacional e atribuição correta das etapas foram revalidados deterministicamente. Filtro temático rejeita Conta Digital como solução para conectividade; procedimentos de contratação precisam de evidência de ação/canal. São proteções limitadas, não verificador universal de afirmações.

O QA criou20 cenários de desenvolvimento e10 de validação,14 multi-turn; captura live registra três repetições, versão, erros, fallbacks e checkpoints. São testes ainda não executados com modelo real. A disponibilidade compartilhada do dataset impede alegar segredo absoluto do conjunto reservado.

Frontend: formulários por papel, polling ordenado, limpeza ao sair, proteção contra respostas de sessão anterior, Markdown por DOM e links http(s). Apenas revisão estática/sintaxe neste ambiente. Fallback é visível quando indicado pelo backend; texto é preservado em falha. Retry atualiza histórico antes de permitir reenvio manual, evitando retry cego.

## Integridade histórica

O ZIP original e anexos não foram alterados. Capturas live prévias permanecem históricas em evidence/historical/. Não representam o código candidato. Índice real anexado não foi reingerido neste ambiente: reconstruir para validar metadados/modelo/corpus atuais. Não há screenshot fornecido do chat entre os cinco anexos desta tarefa.

## Fechamento local

Siga COMECE_AQUI.md, README.md e PRE_SUBMISSION.md. Rodar os datasets live não atribui qualidade automaticamente: pontue cada caso contra fontes completas, registre avaliador e denominadores. Rejeição ou alteração de produção exige reexecução dos testes afetados e novo hash/ZIP.
