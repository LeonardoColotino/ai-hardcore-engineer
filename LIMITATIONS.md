# Limitações atuais

- Catálogo de soluções depende dos trechos recuperados, pode ser parcial e pouco explicativo.
- "Como funciona o Link" pode apresentar um tutorial em vez de uma explicação geral concisa; passos aparecem com números isolados.
- Perguntas ambíguas como "Como funciona um produto?" podem cair em busca genérica/handoff, em vez de esclarecimento.
- Continuação de produto foi validada em um cenário; memória de qualquer funcionalidade/paráfrase não é garantida.
- Modelo llama3.2:3b gerou associações incorretas em prose. O perfil recomendado é evidence; os bloqueios não provam que todas as alucinações serão detectadas.
- Revisor pode cobrar detalhes não pedidos ou aprovar relações erradas. Verificações de citações são restritas a condições explicitamente checadas no servidor.
- Rótulo de produto por seção/página e filtro lexical não são compreensão semântica universal; seções mistas podem permanecer sem atribuição.
- Dados de suporte e telemetria são sintéticos e fixos; não há integração financeira real. "Último" corresponde à ordenação dos registros demonstrativos, não a uma consulta ao banco real do cliente.
- Latência depende de hardware, carga, contexto e chamadas ao modelo. A interface já mostrou aviso de timeout após resposta/ticket concluídos; atualize o histórico antes de reenviar.
- Usuário confirmou handoff e encerramento no navegador, mas não há vídeo nem teste de carga da operação.
- Consultas web e ingestão dependem de internet, páginas de terceiros e controles limitados de URL/DNS. Snapshots são históricos; não garantem tarifas vigentes.
- O supervisor é limitado em passos e estratégias; não é equivalente à delegação dinâmica irrestrita de outros projetos.
- Opcionais GGUF, cross-encoder, endpoint compatível e IdP OIDC não têm execução real aprovada neste candidato.
- Sem garantia de nota, produção, segurança certificada ou taxa geral de qualidade. Veja VALIDATION_REPORT.md para procedência dos resultados.
