# Especificação do candidato 2026-10-15

Evoluir o snapshot anexado, preservando API autenticada, SQLite, interface e testes.
Ciclo limitado: baseline → correções → QA → revisão independente → correções → ZIP.
Parar após corrigir falhas locais reproduzidas; serviços ausentes são bloqueios, não aprovação.

Contratos: identidade vem da credencial; planos tipados só escolhem especialistas permitidos;
cada tarefa conserva sua resposta validada mesmo que outra falhe. Diagnóstico público é uma
projeção allowlisted de fixture de terminal, nunca texto da conta. Consulta web tem gate no
servidor. Ticket ativo suspende ferramentas. Reenvio com chave idempotente não duplica turno.
Traces e feedback exigem ownership; não armazenar mensagem/resultado privado na telemetria.
RAG valida HTTPS/hosts/redirecionamento e compatibilidade do índice. Procedimentos não serão
artificialmente limitados a 45 palavras. Falta de evidência permanece explícita.

Aceite: suíte herdada aplicável e regressões novas sem falha; resultados parciais preservados;
isolamento/handoff/duplicidade testados no caminho de produção; registro separado de fakes,
API/SQLite reais, LLM real, Docker e revisão semântica. Nenhuma nota estimada ou runtime inventado.
