**# PROMPT MASTER — AI Hardcore Engineer: auditoria, evolução e validação rigorosa da V3**



**## Como usar este prompt**



Estou anexando o ZIP atualizado do projeto \`ai-hardcore-engineer-v3\`, o desafio original, o feedback da V2 e o último resultado de avaliação com Ollama. Leia este documento inteiro e execute o trabalho solicitado; não se limite a responder com um plano ou a reescrever este prompt.



O objetivo é uma solução tecnicamente sólida para buscar uma avaliação de **\*\*9,5/10 ou superior\*\***. Essa é uma meta pessoal, não uma nota garantida. Não invente uma rubrica oficial, não prometa essa nota e não atribua excelência com base apenas em quantidade de código, agentes ou testes.



**\*\*Não confunda os agentes de desenvolvimento abaixo com os agentes que devem existir dentro da aplicação.\*\*** Quero tanto uma aplicação multiagente funcional quanto uma execução de desenvolvimento com responsabilidades separadas de implementação, testes e validação.



\---



**## 1. Missão, autorização e limites**



Atue como responsável técnico pela evolução da V3. Audite o código real, transforme os problemas em requisitos verificáveis, implemente correções proporcionais, melhore o chat, execute a validação possível e entregue o código completo, empacotado e documentado.



Trabalhe em uma nova pasta ou branch de evolução. Preserve o ZIP original como baseline. Reutilize componentes bons; substitua componentes deficientes quando houver justificativa. Reconstrução total somente se a auditoria demonstrar que é a alternativa mais segura e simples. Não exclua meu projeto de trabalho.



Pode criar arquivos, refatorar, executar testes locais e preparar artefatos autonomamente. Não peça confirmação a cada arquivo. Minha intervenção só é necessária para informação indispensável, credenciais, custos ou publicação externa não autorizada. Não faça push para main, deploy público, consumo de API paga ou envio de mensagens a terceiros sem autorização explícita. Credenciais que faltam não são motivo para interromper trabalhos independentes delas.



Não continue indefinidamente: use ciclos limitados de correção, critérios fixados antes da implementação e um registro claro de bloqueios. Nunca diminua um critério para declarar sucesso.



**## 2. Materiais e hierarquia de evidências**



Materiais esperados:



1\. Desafio original: fonte dos requisitos obrigatórios e da submissão.

2\. Feedback da V2: lacunas e critérios efetivamente observados pelo avaliador.

3\. ZIP atualizado da V3: fonte principal do estado atual do código.

4\. Último \`live_responses.json\`, ou seu conteúdo em Markdown: evidência histórica da avaliação com modelo real.

5\. Este prompt: requisitos adicionais e processo de execução.

6\. Imagem do chat, se disponível: referência visual; não presumir que você conseguiu lê-la.



O desafio original prevalece em caso de conflito. Inspecione código e resultados antes de confiar no README. Leia os anexos integralmente. Se houver arquivo ausente, identifique a lacuna e prossiga com o que é verificável. Se o JSON foi colado em Markdown, preserve o original e registre qualquer normalização necessária para leitura; não modifique respostas para melhorar resultados.



**\*\*O último relatório live foi gerado antes de algumas correções posteriores.\*\*** Não o apresente como validação da versão final do ZIP. Correlacione versão do código, configuração, data e resultados. Reexecute os casos na versão candidata quando possível.



O repositório de referência é \`https\://github.com/LeonardoColotino/ai-hardcore-engineer\`. O ZIP anexado pode conter mudanças ainda não publicadas e prevalece como baseline desta tentativa. Não dependa de acessar GitHub se o ZIP for suficiente.



**## 3. Contexto e ambiente atual**



\- Desenvolvimento principal: Windows, PowerShell e Python **\*\*3.12.10\*\***.

\- Pasta usada: \`C:\Users\joaol\Desktop\Codigos\ai-hardcore-engineer-v3\`.

\- \`python\` funciona, mas o launcher \`py\` não estava disponível.

\- Provedor inicial: **\*\*Ollama local\*\***, sem exigir API paga.

\- Modelos instalados: \`llama3.2:3b\` e \`nomic-embed-text:latest\`.

\- Ollama acessível em \`http\://localhost:11434\`; API/chat em \`http\://127.0.0.1:8000\`.

\- \`REQUEST_TIMEOUT_S=120\` e \`RAG_TOP_K=2\` foram usados durante os testes locais; confirme a configuração disponível, não trate esses valores como necessariamente ideais.

\- Foram relatados **\*\*64 testes passando no Windows\*\***, com um aviso de depreciação TestClient/httpx, e **\*\*17 cenários offline passando\*\***. Isso é histórico informado pelo usuário, não uma execução sua.

\- Ingestão real processou cinco URLs Getnet e inicialmente produziu 23 chunks com Ollama embeddings; depois a limpeza foi alterada e o índice reconstruído. Conteúdo e quantidade atuais precisam de conferência.

\- Login, histórico e ciclo operador → resposta ao cliente → CLOSED funcionaram manualmente.

\- \`.venv\` foi removida durante a preparação do ZIP. Oriente recriação, sem supor que ela existe. Não apagar outros arquivos de trabalho.

\- Dados são fictícios; autenticação pode ser simples e demonstrativa, mas identidade e autorização devem ser reais. Não transformar o desafio em um projeto corporativo excessivamente complexo.



Ollama não é uma imposição do desafio. Mantenha-o como opção padrão inicial e preserve uma interface de provedor substituível. Não confunda Ollama, servidor de inferência, com o modelo que ele executa. Não substitua provedor, baixe modelos enormes ou use serviços pagos silenciosamente.



**## 4. Problemas conhecidos que devem virar regressões**



**### 4.1 Geração e evidências**



O modelo inicialmente dizia não ter informação sobre Link de Pagamento mesmo quando o contexto tinha os passos de criação. Depois passou a responder, mas:



\- Misturava cartão virtual e antecipação da Conta Digital com benefícios do Link de Pagamento.

\- Inventava exigência de conta Getnet para o comprador.

\- Tratava “mantenha o aplicativo atualizado” e QR Code de atualização como funcionalidades financeiras.

\- Listava “Confira os benefícios da Get Conta” como se fosse outro produto.

\- Confundia contratar/aderir ao serviço com criar/configurar um link após acesso à conta.

\- Produzia listas repetidas, termos publicitários sem explicação e informações irrelevantes à pergunta.



Não resolva isso só acumulando instruções no prompt. Revise limpeza, estrutura dos chunks, seleção de fontes, relevância, distinção entre produtos e verificação das afirmações. Contratação só pode ser explicada com evidência de contratação. Na ausência dessa evidência, informe a limitação e ofereça fonte oficial ou handoff apropriado, separando eventual orientação de uso.



**### 4.2 Roteamento e ferramentas**



\- “Como contratar essa solução?” foi encaminhada ao Support e respondeu sobre depósito porque havia “pagamento” no contexto do produto.

\- O LLM classificava incorretamente casos claros apesar de alta confiança declarada.

\- O motivo de roteamento incluía afirmações comerciais inventadas, embora devesse explicar apenas a intenção.

\- Consulta geral atual às vezes escalava sem sequer executar web search; em outra execução tentou web search e não encontrou evidência.

\- Pedidos explícitos de humano às vezes passaram por Support desnecessariamente.



A palavra “pagamento” isolada não justifica executar ferramenta de saldo/depósito. Decisões devem considerar intenção, contexto autorizado e evidência, com fronteiras claras para ferramentas. Confiança autodeclarada do modelo não prova correção.



**### 4.3 Memória**



\- “Essa solução” funcionava em alguns casos, mas “esse link” não era reconhecido.

\- Foi incluída uma regex para essa referência; ela não constitui memória conversacional geral.

\- O supervisor inferia uma lista fixa de produtos ao detectar “soluções”; confira se os candidatos vêm realmente da conversa e se a lista inclui os produtos apresentados.

\- Memória não pode depender de uma lista crescente de expressões exatas ou perder contexto por simples reformulação.



**### 4.4 Codificação**



\`evaluation.live\` usava \`Path.read_text()\` e \`write_text()\` sem encoding. No Windows, o dataset UTF-8 foi lido como outra codificação, gerando \`soluÃ§Ã£o\`, e a saída foi gravada fora de UTF-8. Isso invalidou parte da avaliação.



A correção explícita de UTF-8 melhorou L1, mas não corrigiu todas as falhas. Audite **\*\*toda leitura/gravação de texto\*\***, não somente esse runner. Diferencie problema do arquivo, problema de transporte e exibição do PowerShell.



**### 4.5 Colaboração e abstention**



Support → Knowledge executou e transmitiu um diagnóstico real, mas Knowledge recuperou página da Conta Digital sem orientação técnica de conectividade. A resposta dizia não encontrar informação e, mesmo assim, a requisição terminava com \`escalated=false\` e aparência de resolução.



Similaridade alta com uma página Getnet não prova relevância para o problema. Não trate uma resposta sem evidência como resolução bem-sucedida. Exija diagnóstico, resultado de retrieval, decisão de resolução e eventual handoff coerentes.



**### 4.6 Handoff e observabilidade**



Tickets reais existiam, mas respostas e metadata herdadas da V2 diziam:



\- “this demo does not create or send a support ticket”;

\- \`ticket_created=false\`;

\- \`handoff_status=recommended\`;

\- agentes duplicados, como \`['escalation', 'escalation']\`;

\- ferramenta \`human_handoff\` atribuída à etapa de Knowledge, apesar de ter executado web search.



Corrija a fonte desses estados. Não apenas remova o texto errado ou preencha flags sem comprovar persistência. Mensagem, status HTTP, banco, metadata e UI devem representar o mesmo resultado.



**### 4.7 Desempenho e fallback**



Foram observadas requisições de aproximadamente 110–155 segundos e fallback extrativo. O erro do LLM era descartado. A última correção registrou somente o tipo de exceção e distinguiu fallback de geração.



Investigue router LLM, embeddings, retrieval, geração, tamanho do contexto, carregamento do modelo, competição por recursos e limites de saída. Não concluir que “Ollama é ruim” sem medição. Não apenas aumentar timeout. Não representar fallback como avaliação bem-sucedida de geração.



**### 4.8 Patches posteriores ainda precisam de auditoria**



Foram feitas correções locais no prompt, limpeza HTML, regex de referência, regra de contratação no router, UTF-8 do runner e um teste de “esse link”. Uma verificação lexical foi adicionada para rejeitar resposta que confunde contratação com criação.



Audite esses patches. A verificação lexical é proteção limitada, pode ter falsos positivos/negativos e não deve ser tratada como grounding geral. Substitua remendos frágeis por decisões estruturadas e invariantes quando isso trouxer benefício comprovável.



**## 5. Equipe de desenvolvimento obrigatória**



Use agentes de desenvolvimento separados **\*\*se a plataforma oferecer subagentes reais\*\***. Estou autorizando explicitamente delegação para estas funções:



**### Agente A — Implementação / arquitetura**



Audita o código, propõe arquitetura, escreve especificações, implementa e corrige defeitos. Não se autoaprova como validador final.



**### Agente B — Testes / QA**



Deriva testes do desafio, feedback, especificações e falhas históricas. Cria cenários positivos, negativos e adversariais; executa testes; registra defeitos reproduzíveis e evidências. Desenvolve também casos novos que não sejam cópias dos exemplos já ajustados.



O agente de testes pode editar testes e fixtures, mas não alterar código de produção para fazer um teste passar sem registrar o defeito e encaminhá-lo ao implementador. Critérios de negócio não devem ser ajustados à implementação existente.



**### Agente C — Validação / revisão independente**



Revisa comportamento, código, resultados brutos, documentos e UI da versão candidata. Pode rejeitar uma entrega com testes verdes quando respostas, evidências ou estados forem incorretos. Confirma quais testes realmente foram executados e quais integrações seguem pendentes.



O validador não deve simplesmente repetir o relatório do implementador, nem usar somente os mesmos asserts do QA. Confira fatos contra trechos completos, execução e estado persistido. Registrar um julgamento de IA como tal; não chamá-lo de avaliação humana nem de nota oficial.



**### Coordenação**



Um responsável integra resultados, organiza prioridades e entrega o pacote. Em workspace compartilhado, evite agentes editando o mesmo arquivo ao mesmo tempo; atribua donos de arquivos/áreas e passe artefatos explicitamente. Não delegue trabalhos independentes que dependem de código ainda não estabilizado como se já fossem verificáveis.



Se não houver subagentes reais, informe isso e realize as funções sequencialmente, com relatórios separados e checklist independente. **\*\*Não finja ter criado três agentes nem apresente autoavaliação sequencial como revisão externa.\*\***



**## 6. SDD obrigatório, antes da implementação**



Use **\*\*Spec-Driven Development\*\***, não SDK. Produza ou revise documentos distintos, específicos e úteis:



\- \`AUDIT_BASELINE.md\`: código, anexos, arquitetura, testes atuais e falhas reproduzidas.

\- \`SPEC.md\`: comportamentos, limites, contratos e requisitos identificados.

\- \`ARCHITECTURE.md\`: componentes, dataflow, trust boundaries e decisões.

\- \`ACCEPTANCE_CRITERIA.md\`: critérios positivos, negativos e mensuráveis.

\- \`TEST_PLAN.md\`: cenários, níveis, fixtures, ambientes e responsabilidade QA.

\- \`REQUIREMENTS_MATRIX.md\`: requisito → código → teste → execução → evidência → limitação.

\- \`IMPLEMENTATION_PLAN.md\`: prioridades, dependências, checkpoints e timebox.



Use IDs como REQ-MEM-001, REQ-ROUTE-001, REQ-GROUND-001, REQ-HITL-001, REQ-ENC-001, REQ-PERF-001 e REQ-UI-001. Cada requisito deve ter objetivo, justificativa, aceite, teste positivo, teste negativo, responsável e estado.



Não copie o mesmo texto em todos os documentos nem declare SDD somente por criar arquivos Markdown. Requisitos existentes válidos devem permanecer; mudanças precisam de justificativa e revisão do validador.



Primeiro ciclo core: **\*\*no máximo 60 minutos\*\***, priorizando causas mais graves e regressões. É um timebox de um ciclo, não um limite para toda a entrega. Registre início/fim observados e pendências; não invente duração. Se não couber, continue em ciclos documentados, sem baixar o nível de aceite.



**## 7. Requisitos da aplicação**



Preserve todos os obrigatórios do desafio original. No mínimo:



\- Router/Supervisor como entrada e coordenador.

\- Knowledge com RAG Getnet e web search geral.

\- Support com pelo menos duas ferramentas próprias e identidade autenticada.

\- HTTP API FastAPI e contratos Pydantic.

\- Docker e documentação reproduzível.

\- Estratégia e implementação de testes.

\- README e preparação de vídeo/repositório conforme desafio.



A aplicação também deve manter:



\- Escalation/Human Handoff operacional e persistente.

\- Memória multi-turn por sessão autenticada.

\- Colaboração sequencial real entre especialistas.

\- Logs estruturados, avaliação e falhas explícitas.

\- Interface de chat funcional e área de operador.



Não introduza framework agentic, banco vetorial ou mensageria só para aparentar complexidade. Funções diretas e SQLite são aceitáveis se os critérios forem satisfeitos. Documente limites de demonstração versus produção.



**## 8. Orquestração, roteamento e memória**



Defina um estado de conversa explícito com intenção atual, produto/entidade escolhida, candidatos ambíguos, etapa, histórico relevante, resultado dos especialistas e eventual ticket. Persista o estado necessário para continuidade entre processos/requisições e reinícios.



Requisitos:



\- Identidade derivada de autenticação, nunca do texto ou do LLM.

\- Sessão inexistente/alheia não acessível; ausência de ID cria nova conversa segundo contrato.

\- Contexto recuperado dentro de janela/orçamento documentado; histórico consultável.

\- Nova conversa não herda a anterior; usuário diferente nunca herda dados.

\- Referência ambígua pede esclarecimento, incluindo produtos efetivamente apresentados.

\- Referência clara continua sem pergunta redundante.

\- Corretamente distinguir produto, pagamento de uma venda, contratação, criação do link e suporte de máquina.

\- Classificação por LLM validada estruturalmente; política/contratos impedem escolhas incompatíveis com ferramentas ou intenção clara.

\- Motivo do roteamento explica decisão, sem inventar fatos comerciais.

\- Plano limitado, sem loops; orçamento de etapas/chamadas/tempo.

\- Segundo especialista consome resultado útil do primeiro e isso é verificável.

\- Evitar enviar todos os pedidos claros ao LLM se isso apenas acrescenta custo, latência e erro.



Cenários multi-turn devem incluir paráfrases, mudança de assunto, correção pelo usuário, referência após uma mensagem intermediária e retomada após reinício. Uma regex isolada não é evidência suficiente de memória.



**## 9. RAG, relevância e grounding**



Pipeline esperado: ingestão → limpeza estrutural → chunking → embeddings → armazenamento → recuperação → filtragem/relevância → geração → verificação → resposta ou abstention/handoff.



Exija:



\- URLs oficiais Getnet válidas; conteúdo e datas identificáveis.

\- Remoção de menus, formulários, modais e componentes de interface sem descartar conteúdo útil por acidente.

\- Preservação de títulos/seções e limites de frases/itens; evitar chunks começando no meio de palavra.

\- Deduplicação, metadados, IDs de chunks, origem, seção/produto e versão do corpus.

\- Persistência e reconstrução reproduzível, com compatibilidade de embeddings e dimensões.

\- top_k e threshold configuráveis e escolhidos por avaliação, não para acertar um único exemplo.

\- Relevância temática além de “menciona Getnet”; distinguir Conta Digital de Link de Pagamento e conectividade.

\- Recuperação com fontes e trechos suficientes para revisão de cada afirmação importante.

\- Tratamento de índice ausente, corrompido ou desatualizado e fontes indisponíveis.

\- Índice/hash demo e seed claramente separados do corpus real; nunca usar seed como evidência oficial.

\- Documentos como dados não confiáveis; instruções maliciosas não mudam identidade, ferramentas ou políticas.

\- Sem garantia factual baseada somente em score vetorial, URL ou presença de trecho na resposta.



A verificação de grounding deve diferenciar resposta fundamentada, parcialmente fundamentada, sem evidência e falha de geração. Afirmações críticas de contratação, taxas, elegibilidade, prazos e garantias exigem evidência aplicável. Evite copiar disclaimers de outro produto como condição do produto consultado.



Não remova informações reais sobre RNE, carrinho ou frete simplesmente porque parecem inesperadas: confira o documento. Também não aceite essas afirmações só porque uma fonte foi exibida.



Abstenção não deve ser utilizada como resposta universal para obter métricas de segurança altas. Meça também a capacidade de responder aos casos que têm evidência suficiente.



**## 10. Support, autenticação e handoff**



Use dados fictícios. Tools devem validar escopo no backend. Identificadores de cliente/conta produzidos pelo LLM não são autorizadores. Pergunta sobre contratação de Link de Pagamento não pode disparar payment_status por conter “pagamento”.



Testar customer_lookup, transaction_lookup e payment_status ou equivalentes; erros, registros vazios, acesso cruzado e associação correta ao cliente autenticado. Logs não devem expor dados desnecessários.



Handoff completo:



1\. Decisão e motivo registrados.

2\. Ticket persistente ligado à sessão/cliente correto.

3\. Protocolo e status coerentes na API/UI.

4\. Operador autorizado assume.

5\. Resposta humana persistida e visível no histórico.

6\. Resolução e fechamento obedecem máquina de estados.

7\. Cliente consulta somente próprios tickets.

8\. Atribuição concorrente não permite dois donos contraditórios.



OPEN → IN_PROGRESS → RESOLVED → CLOSED ou estados equivalentes documentados. Proibir saltos, responder ticket alheio sem permissão e repetir transições inválidas. Considerar idempotência de criação/reply/retry para evitar duplicatas.



Não marcar ticket_created=true antes da confirmação do banco. Quando ticket existir, texto e metadata não podem dizer “apenas recomendado”. Agentes envolvidos e tools por etapa devem refletir a execução real, sem duplicações artificiais.



SQLite e tokens assinados demonstrativos são suficientes se autorizadores forem corretos; não exigir infraestrutura enterprise. Segredos por ambiente, \`.env.example\` sem segredos, senha demo explicitamente não produtiva e provisionamento simples. Falha de configuração deve explicar como corrigir sem imprimir credenciais.



**## 11. LLM, timeout e desempenho**



Preserve uma interface de provedor e Ollama como inicial. Router e geração podem ter configurações diferentes se justificado; embeddings também precisam de timeout/batch próprios e rastreáveis.



Implemente limites coerentes de contexto, saída, chamadas e duração. A requisição não pode parecer travada indefinidamente. Não configure retries sem orçamento e risco de duplicação. Se houver retry, registre tentativa e motivo.



Classifique erros: timeout, conexão, status HTTP, resposta inválida, JSON inválido, modelo ausente e provider disabled. Registre campos seguros com request_id/etapa; não descarte silenciosamente LLMError. Fallback deve ser explícito para UI e avaliação, com causa distinguível, nunca apresentado como geração real.



Meça separadamente router, embedding, retrieval, geração e persistência; observe warm/cold start e concorrência. Registre modelo/digest, hardware disponível, opções de inferência, tamanho de contexto, número de chamadas e tokens quando o provider informar.



Meta inicial de usabilidade: p95 de chat com modelo aquecido ≤ 60 segundos em carga serial representativa; timeout total configurável e erro legível. **\*\*Essa é uma meta de projeto a verificar, não uma promessa sobre o notebook.\*\*** Fixe medição e orçamento no SDD. Se hardware impedir atingir a meta, documente gargalo e alternativas sem afirmar aprovação nem esconder outliers.



Não aumente timeout para mascarar desenho ineficiente. Não afirme que GPU é usada sem observar execução. Não force upgrade/download de modelo sem avaliar memória disponível e autorização. API hospedada permanece opção arquitetural futura, sem consumo pago obrigatório nesta entrega.



**## 12. Interface do chat: melhoria obrigatória e funcional**



Melhore o frontend real, integrado à API. Não entregar mockup, screenshot conceitual ou frontend isolado. Preserve solução leve se suficiente; não hospede um chat desconectado do backend para simular funcionamento.



Direção visual: interface moderna, sóbria e organizada, em português, com vermelho como destaque e fundos neutros; desktop e mobile. Não presumir identidade visual oficial da Getnet sem ativos fornecidos.



Funcionalidades e acabamento:



\- Login de demonstração simples, erros claros e papéis cliente/operador visivelmente distintos.

\- Sidebar com nova conversa, títulos úteis em vez de somente hashes e indicação da conversa ativa.

\- Bolhas legíveis de usuário, assistente e operador; espaçamento e contraste adequados.

\- Markdown seguro para listas e negrito; sem exibir \`\*\*\` ou barras de escape como formatação final.

\- Sanitização de conteúdo e links; nunca usar HTML do modelo sem proteção XSS.

\- Fontes deduplicadas por URL no display, com títulos curtos e legíveis, preservando os chunks na evidência técnica.

\- Evitar título duplicado “Fonte: ... Fonte: ...”.

\- Compositor com enviar, Enter para enviar, Shift+Enter para quebra, sem envios duplicados.

\- Estado de carregamento e tempo de espera perceptível; feedback de falha/fallback sem expor stack trace.

\- Manter mensagem digitada quando o envio falhar e permitir retry seguro.

\- Histórico persistente após login/reload, sem misturar sessões.

\- Tickets com protocolo, motivo resumido, resposta humana e badges OPEN/IN_PROGRESS/RESOLVED/CLOSED traduzidos.

\- CLOSED é estado, não botão do cliente. Somente operador vê ações autorizadas de assumir/responder/fechar.

\- Área de operador com fila e formulário de resposta integrado; preferir formulário da interface a prompt() do navegador.

\- Atualização de status/resposta por polling controlado ou outra solução simples, com indicação de atualização e sem regressão de estado por respostas fora de ordem.

\- Detalhes de agentes/fontes acessíveis em painel opcional, sem poluir a conversa com implementação.

\- Navegação por teclado, foco visível, labels, mensagens acessíveis, contraste e mobile sem overflow.

\- Estado vazio, erro, carregamento, resposta curta/longa, fontes e conversa com ticket testados.



QA visual deve usar navegador real em desktop e mobile, por exemplo 1280×800 e 390×844, com inspeção de screenshots e comportamento. Não afirmar aprovação visual baseada somente em node --check ou HTML 200. Se navegador estiver bloqueado, registrar pendência e entregar script de smoke para execução local.



Não exigir URL pública para validar UI local. Publicação depende de autorização/infra; nunca expor Ollama diretamente à internet.



**## 13. Testes: responsabilidades e cobertura necessária**



Preserve as regressões válidas e acrescente testes que reproduzam defeitos **\*\*antes da correção\*\***. Teste de uma proteção deve falhar se a proteção for removida. Não exigir contagem arbitrária de testes; prefira comportamento significativo.



**### Determinísticos**



Unitários, contratos, integração de API, autorização, persistência, falhas e browser E2E quando disponível. Usar banco/índice temporários e isolamento; não poluir conversas/tickets do usuário. Testar ao menos:



\- Acertos/erros do router e confiança LLM enganosa.

\- LLM tenta mandar contratação ao Support; política evita tool errada.

\- “Pagamentos das minhas vendas” versus “Link de Pagamento”.

\- Referência “esse link”, “essa solução”, produto único e vários produtos, mudança de assunto.

\- Continuidade por múltiplas requisições e após reinício/processo novo.

\- Acesso alheio a sessões/tickets e user_id manipulado.

\- Token inválido/expirado, papel errado e configuração ausente.

\- Tools com registros vazios/indisponíveis e identidade correta mesmo com texto malicioso.

\- Sequência Support → Knowledge com dado consumido de fato.

\- Resultado sem orientação técnica não marcado como resolvido.

\- Tickets transacionais, atribuição, reply, CLOSED e coerência com API/metadata/UI.

\- Timeout/provider offline/model response inválida e fallback classificado.

\- UTF-8 no Windows: leitura, gravação e round-trip de “soluções”, “contratação”, “não”, “ç”.

\- Limites de execução/rate e ausência de loops.

\- Documentos maliciosos, XSS, fontes/links não seguros e vazamento de segredos.

\- Índice ausente/corrompido e provider de embeddings incompatível.

\- Citação falsa, evidência irrelevante, abstention, fallback e texto com contratação confundida com uso.

\- UI: login dos dois papéis, conversa, resposta humana, status atualizado e nenhuma ação de operador exposta ao cliente.



Não instalar dependências novas só para silenciar warnings sem avaliar compatibilidade. Corrigir depreciações quando viável e registrar as que persistirem.



**### Avaliação com LLM real**



Testes determinísticos não aprovam qualidade semântica. Use dataset versionado com contexto, resposta esperada/rubrica, evidência e comportamentos proibidos; prompts não devem conter respostas específicas dos testes.



Casos obrigatórios incluem L1–L8 históricos, Link/Conta, contratação vs criação, exigência inventada para comprador, produto não sustentado, dado atual, conectividade sem evidência, injection, outra conta e pedido de humano. Acrescente paráfrases e sequências novas produzidas pelo QA.



Use conjunto de desenvolvimento e conjunto de validação reservado. Sugestão mínima para esta entrega: 20 cenários de desenvolvimento e 10 de validação, com ao menos dez cenários multi-turn no total e cobertura negativa/adversarial. Defina a seleção antes da correção. Não prometer independência de holdout se o implementador o utilizou para ajustar respostas; registrar eventual contaminação.



Repetir pelo menos três vezes os fluxos críticos com modelo real, distinguindo resultados de cada execução. Toda captura registra versão/corpus/configuração/modelo/horário e contém resposta, fonte/evidência, agente/tools, duração, geração ou fallback e erro. Não gravar credenciais.



A avaliação deve verificar afirmações contra trechos completos, intenção, adequação, produto correto, contexto, tools, abstention e falhas. Classifique julgamentos como humano, agente de IA, heurística ou teste determinístico. Qualquer LLM-as-judge deve ser identificado e suas limitações documentadas; use verificação determinística para segurança e estados, e amostragem/revisão factual para qualidade.



**## 14. Critérios de saída: fixar antes e não maquiar depois**



Os critérios abaixo são metas internas de engenharia, não a rubrica oficial nem equivalência automática a 9,5/10:



1\. Todos os obrigatórios do desafio atendidos e ligados a evidência.

2\. Zero defeitos críticos de isolamento, vazamento, ferramenta indevida ou estado persistido contraditório.

3\. Todos os testes determinísticos pertinentes passam; nenhuma falha conhecida ocultada por skip/xfail sem justificativa e pendência explícita.

4\. Nenhuma afirmação crítica sem apoio sobre taxas, elegibilidade, requisitos de conta, prazos ou contratação nos casos críticos reservados.

5\. Nos casos com evidência suficiente, taxa de resposta útil e fundamentada ≥ 90%; recusas/fallback não contam como respostas úteis apenas por serem seguras.

6\. Roteamento e seleção de tools ≥ 95% no conjunto de avaliação final, com zero seleção indevida de tools de conta nos casos de produto/contratação.

7\. Todos os cenários críticos de memória, handoff e autorização passam nas repetições; avaliar cada cenário e não esconder uma falha crítica na média.

8\. Groundedness e relevância médias ≥ 1,8/2 nas dimensões aplicáveis, com rubrica 0=incorreto, 1=parcial, 2=atende; nenhuma dimensão crítica com zero. Documentar avaliador e justificativa por caso.

9\. Fallbacks, erros e timeout têm denominador e métricas próprios; nunca excluir silenciosamente casos difíceis ou tentativas falhas.

10\. UI aprovada em comportamento e visual quando navegador disponível; Docker build/run/health/persistência validados quando runtime disponível.

11\. Latência medida contra orçamento definido; gargalos e pendências materiais impedem aprovação integral até revisão.

12\. Agente validador aprova o candidato com evidências; opinião do implementador não substitui aprovação.



Se não for possível executar Ollama/Docker/browser no ambiente, execute os testes viáveis e entregue uma bateria local automatizada. Marque as integrações como **\*\*pendentes\*\***, não aprovadas. Coletar resultados locais do usuário é aceitável se identificado como execução externa. Não usar mocks como prova da integração real.



**## 15. Ciclo de implementação, QA e rejeição**



Para cada ciclo:



1\. QA reproduz o problema e registra ticket técnico com requisito, severidade, passos, esperado/observado e evidência.

2\. Implementador corrige a causa e apresenta mudança revisável.

3\. QA executa testes afetados e regressões necessárias.

4\. Validador revisa resultado bruto, qualidade e invariantes; aceita ou rejeita com justificativa.

5\. Rejeição reabre a correção; não modificar a expectativa só para aprovar.



Após componentes estabilizados, execute validação completa do candidato final. Uma alteração posterior invalida evidências afetadas e exige rerun correspondente.



Use até **\*\*cinco ciclos principais por causa persistente\*\***, registrando progresso. Se não houver melhora mensurável ou faltar recurso externo, pare a tentativa improdutiva, documente causa/bloqueio e avance nas tarefas independentes. Não executar loop infinito nem prometer “refazer até garantir 9,5”. Critérios não atingidos significam entrega parcial/pending, não conclusão inventada.



Toda divergência entre resposta, tools, flags, banco e UI é defeito. Review deve encontrar também inconsistências de documentação e dados do corpus, não somente exceções de código.



**## 16. Docker, Windows e reprodutibilidade**



\- Python suportado e dependências fixadas/reproduzíveis, verificadas em instalação limpa quando possível.

\- Scripts Windows usando \`python\`/Python explícito da venv, sem exigir \`py\` se não existir.

\- \`.env.example\` suficiente para configuração; provisionamento demo e recuperação de credenciais bem explicados.

\- Docker sem root, healthcheck, volume para estado/índice, serviço de modelo separado e endereço host documentado.

\- Início sem índice deve ter comportamento previsível; não esconder falta de prontidão no healthcheck.

\- Diferenciar liveness, readiness e dependência LLM quando necessário. Provider configurado não prova provider acessível.

\- Validar rebuild/restart e retenção de sessões/tickets; não apagar volume no teste sem preservar dados do usuário.

\- Não alegar Docker validado após somente ler Dockerfile.

\- Package com todos os arquivos, excluindo \`.env\`, venv, caches, credenciais reais e bancos de trabalho. Dados demo/versionados e fixture necessários devem ser incluídos.

\- Resultados relevantes de avaliação devem ser mantidos com versões, UTF-8 e sem segredos; não excluir todas as evidências por engano ao limpar o ZIP.



**## 17. Observabilidade e relatórios**



Registre request_id, session_id, usuário pseudonimizado, intenção/produto quando adequado, plano, agente, tool, motivo, fontes/chunks, duração por etapa/total, erro/retry, generation_kind, fallback, abstention, ticket e outcome final.



Métricas mínimas: sucesso técnico, resolução efetiva, respostas fundamentadas, abstention, escalonamento, fallback, falhas por tool/provider, latência p50/p95, chamadas LLM por requisição e resultados de avaliação. Defina denominadores. HTTP 200 não significa resolução correta; ticket não significa falha técnica; abstention não significa resposta de qualidade.



Preserve contexto de tracing mesmo em exceções, sem vazamento entre requisições. Não logar tokens, senha, CPF real ou prompts completos com dados sensíveis. Observabilidade local é suficiente, sem serviço pago obrigatório.



Relatórios devem conter comando, ambiente, versão/corpus/modelo, data, resultado, evidência e limitações. Diferenciar implementado, validado, parcial, bloqueado e pendente. Evidência histórica não representa candidato final.



**## 18. Entregáveis obrigatórios**



Entregue:



1\. Código-fonte completo evoluído da V3, em pasta/branch identificada.

2\. ZIP completo funcional, não apenas documentos.

3\. Documentos SDD e baseline auditado.

4\. Testes unitários, integração/API, segurança/falha e browser E2E quando possível.

5\. Dataset, runner offline/live, rubrica e resultados por cenário.

6\. Frontend de chat e operador melhorados e integrados.

7\. Dockerfile/Compose, scripts Windows, \`.env.example\` e setup reproduzível.

8\. README com arquitetura, trade-offs, instalação, Ollama, memória, tools, RAG, tickets, segurança, UI, evals e limites.

9\. \`DEFECT_LOG.md\` com problemas, correções e revalidação.

10\. \`VALIDATION_REPORT.md\` com resultados realmente executados.

11\. \`INDEPENDENT_REVIEW\.md\` com parecer do validador e pendências.

12\. \`REQUIREMENTS_MATRIX.md\` atualizada com evidências.

13\. \`LIMITATIONS.md\`, checklist de submissão e roteiro de vídeo de 5–7 minutos.

14\. Comandos locais para finalizar validações bloqueadas, preferencialmente automatizados.

15\. Resumo claro das mudanças e do que ainda pode prejudicar a avaliação.



Atualize documentação para corresponder ao código entregue. Remova promessas antigas de “100% grounding” baseadas em excerpts e referências a handoff que não cria tickets, se já houver persistência real.



**## 19. Auditoria final e integridade**



O validador responde por requisito: implementado? teste existe? executado onde? passou? evidência está ligada à versão correta? limitações? atende ao desafio? há contradição entre API/banco/UI/docs?



Não:



\- Autoatribuir nota 9,5 ou aprovação oficial.

\- Declarar testes, browser, modelo real ou Docker executados sem evidência.

\- Tornar testes triviais, remover asserts importantes ou reduzir o conjunto para subir médias.

\- Resolver perguntas reais por respostas fixas copiadas dos casos de avaliação.

\- Criar agente decorativo ou segundo especialista que só repete texto.

\- Exibir fontes irrelevantes como suporte factual.

\- Confundir uso do produto com contratação, instrução comercial com funcionalidade ou outro produto com o consultado.

\- Aumentar timeout, regex e proibições de prompt sem investigar causas.

\- Fingir subagentes, revisão humana, holdout independente ou integração pública.

\- Continuar alterando arquivos após gerar o ZIP sem reconstruí-lo e validar as evidências afetadas.



A meta é engenharia verificável. Se critérios críticos não forem atingidos, diga claramente que o projeto ainda não está pronto para submissão integral, mesmo entregando o pacote completo disponível.



**## 20. Instrução de início**



Comece imediatamente pela leitura integral dos anexos e auditoria do ZIP atualizado. Crie a equipe real de implementação, QA e validação se disponível. Execute o baseline, escreva as especificações antes das mudanças e apresente um resumo das decisões.



Depois prossiga autonomamente com implementação, melhoria da UI, ciclos de testes e revisão. Faça atualizações curtas de progresso com achados e bloqueios. Quando depender da minha máquina Windows/Ollama, entregue o comando exato e explique o resultado esperado, evitando edições manuais fragmentadas de muitos arquivos.



Prefira entregar arquivos completos corrigidos ou patches automatizados com backup e verificação, em vez de me pedir repetidamente para colar blocos com indentação. Não solicite que eu envie senhas ou \`.env\`.



Ao final, entregue ZIP, relatórios, matriz e parecer crítico. O trabalho só está integralmente aprovado quando os critérios combinados são satisfeitos e verificados; pendência externa permanece pendência.
