# Candidato 1.4 — última correção focada

149 testes passaram; 17 cenários offline passaram. Nos nove testes novos, oito falharam na versão 1.3 antes da correção e um já passou. Logs em evidence/. Testes de transporte simulam HTTP: não são execução real de Ollama.

## Correções
- Cliente Ollama usa `format` com schema JSON para seleção. IDs pertencem à enumeração dos candidatos existentes; no máximo seis; nenhum campo extra. Temperatura zero. A aplicação mantém validação estrita de formato e referências. Não corrige IDs inventados por aproximação.
- A documentação oficial suporta esse uso: https://docs.ollama.com/capabilities/structured-outputs. O caminho de geração comum permanece separado.
- Candidatos excluem convites genéricos, publicidade institucional, fragmentos que dependem de uma frase anterior e menus de criação quando a pergunta é sobre funcionamento.
- Para perguntas amplas sobre Get Smart/Get Clássica, candidatos precisam conter informação operacional; um convite “Veja como funciona” não vira resposta resolvida.
- Falhas de seleção possuem diagnóstico seguro na metadata: invalid_json, invalid_schema ou invalid_reference. Não incluem saída bruta do modelo, senhas ou prompts.
- README identifica o contrato atual e as limitações. Não alteramos ingestão, banco, autenticação, volumes ou modelos nesta atualização.

## O que os testes não comprovam
Não conhecemos a causa exata das quatro seleções inválidas da captura anterior: a saída bruta não estava no JSON. O schema corrige uma fragilidade identificada no cliente, mas ainda precisa ser testado com o servidor/modelo local. A selecção pode permanecer irrelevante; uma fonte pode ser incompleta ou desatualizada. Não é aprovação final, nota estimada ou garantia de 100%.

Não executamos Docker, Ollama, Windows ou navegador neste ambiente. Não houve revisão por outro agente nesta rodada. Não ajustamos código às perguntas do conjunto validation. O conjunto de desenvolvimento já foi usado repetidamente e não mede generalização. Depois de testar este candidato, executar validation e revisar as respostas contra fontes completas é necessário.

## Critério para seguir ao vídeo
Sem erros de captura, sem fatos inventados nos cenários revisados, sem referências inválidas, instruções completas quando documentadas, nenhuma exposição de outro usuário, encaminhamento coerente e fluxo humano persistido. Se algo falhar, registrar a limitação e corrigir a causa ou reduzir explicitamente o escopo; não esconder a falha nem declarar aprovação pela contagem de testes.
