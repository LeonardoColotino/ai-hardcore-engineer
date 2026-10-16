# Comece aqui

1. Extraia em pasta nova; conserve sua instalação anterior.
2. Siga o quickstart de `README.md` dentro da pasta que contém `requirements.txt`.
3. Configure `.env`, provisione usuários e construa o índice antes de testar Knowledge.
4. Entre como cliente; abra outra janela para `operador` e teste assumir → responder → fechar.
5. Execute os testes e a captura live. Leia `VALIDATION_REPORT.md` antes de apresentar resultados.

Erros comuns:
- `python` ausente: instale Python 3.12 e abra novo PowerShell.
- Ativação bloqueada: use `.\.venv\Scripts\python.exe` diretamente; ativar venv não é necessário.
- Login 503: configure segredo e execute `scripts/init_demo.py`. Não há senha pública padrão.
- Login 401: use a senha do provisionamento; mudar `.env` não troca hashes já provisionados.
- Índice ausente/incompatível: reexecute ingestão com o provedor correto.
- Ollama inacessível: confira `ollama list`, processo local, porta 11434 e host dentro do Docker.
- Resposta de contingência: confira modelo, timeout e fontes; não equivale a resposta LLM validada.
- Ticket aberto: as ferramentas ficam suspensas até resolução humana; operador usa “Ver conversa”.
- Reenvio 409: atualize histórico. Reserva interrompida não é repetida automaticamente para evitar duplicação.

Atualização: pare o serviço, faça backup do SQLite, identidades e índice antes de trocar código.
A inicialização adiciona tabelas sem apagar sessões. Não sobrescreva seu `.env` ou banco com os do exemplo.
