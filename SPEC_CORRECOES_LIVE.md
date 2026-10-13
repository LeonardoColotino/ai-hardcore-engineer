# Correções da rodada de desenvolvimento — especificação antes do código
Baseline: ZIP local atualizado, captura development com 20 casos e 34 turnos. Mudanças não comprovam qualidade do Ollama sem rerun real.

| ID | Comportamento | Positivo | Negativo | Evidência prevista |
|---|---|---|---|---|
| FIX-HTML | Extrair também descrições em div/span; manter blocos | Passos completos | Menu removido | Fixture HTML |
| FIX-SOURCE | Evidência específica ao produto; recuperar candidatos antes de filtrar | Fonte Pix para Pix | Pix não comprova Get Smart | Regressões relevantes |
| FIX-STATE | Estado de intenção/account e comparação, sem identidade do texto | Follow-up depósito, duas máquinas | Obrigado não abre ticket | API temporária |
| FIX-OUTCOME | Abstenção e truncamento não são resolved | Sem informação explicitado | done_reason length não passa como llm completo | Mock transporte |
| FIX-POLICY | Requisitos de comprador só com evidência explícita | Condição documentada | CTA não comprova requisito | Geração não chamada |

Manter 77 testes e regressões anteriores. Não mudar expectativas para ocultar falhas. Schema de retorno generate continua str; finish length gera erro tipado e fallback explícito. Respostas ainda exigem revisão factual; filtros são conservadores, não entailment universal. API, auth e volume state permanecem compatíveis. Pacote novo sem segredos/índice legado; migração usa mesmo projeto Compose para preservar dados. Validação local Docker/Ollama pendente nesta execução.
