# Auditoria de origem e comparação

`evidence/current/input_manifest.json` registra SHA-256/tamanho dos sete anexos.
Base escolhida: ai-hardcore-engineer-v3-evoluido1.0, única versão própria anexada. Não há snapshot V4
separado nem prova de que este ZIP corresponde exatamente à branch v3-1.4 avaliada. A base foi copiada;
o anexo original não foi modificado. Dependências fixadas estão em requirements.txt.

Gabriel: mecanismos de plano estruturado/supervisão, memória, ticket atômico e testes de isolamento
foram examinados. Skywalker: especialistas como ferramentas, histórico tipado, medição de uso e
separação de integração/avaliação foram examinados. Não foi localizada licença de reutilização nos
ZIPs; nenhum código ou identidade dos projetos de referência foi incorporado. Suas notas não são
resultados deste candidato. O README Skywalker contém vídeo: não se inferiu que vídeo não tenha peso.

Problemas observados no próprio snapshot: prompt 45 palavras sem passos; contexto de suporte inteiro
no Knowledge; ticket ativo sem suspender tools; ausência de boundary no web tool; ingestão sem
validação por redirect. Correções e testes correspondentes constam na matriz.

92 testes no baseline; 122 no candidato. Contagem é inventário, não meta nem qualidade semântica.
Ausências dos arquivos de regressão posteriores estão no relatório; cobertura nova é equivalente
apenas aos comportamentos explicitamente testados, não uma restauração dos arquivos ausentes.
