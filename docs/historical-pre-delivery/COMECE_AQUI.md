# Comece aqui

1. Extraia `ai-hardcore-engineer-v4-consolidado` em pasta nova. Não substitua a versão publicada.
2. Siga o README: escolha instalação local ou Docker; configure secrets no `.env` apenas localmente.
3. Inicialize usuários e reconstrua o índice dos snapshots. Eles são históricos; para fontes atuais execute ingestão real.
4. Abra o chat e valide cliente/operador. Modo disabled não é IA gerando respostas.
5. Conecte o Ollama que você já possui e reinicie o servidor.
6. Execute testes, captura live e roteiro manual; preserve falhas e revise respostas completas.
7. Só então atualize evidências e publique em branch nova com sua gravação.

O perfil básico não baixa modelo/reranker. Não existe senha pública: use DEMO_PASSWORD do seu `.env`. Evite vários projetos na porta 8000 ao mesmo tempo. Não apague volumes da V3.
