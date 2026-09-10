"""
Agente responsável por perguntas de conhecimento.

Pode utilizar:
- RAG para perguntas sobre Getnet
- Web Search para perguntas gerais
"""

from app.rag.retriever import retriever
from app.services.llm import llm_service
from app.tools.web_search import search_web


class KnowledgeAgent:

    def is_getnet_question(self, message: str) -> bool:
        """
        Decide se a pergunta deve usar o RAG da Getnet.
        """

        keywords = [
            "getnet",
            "maquininha",
            "máquina",
            "pos",
            "pagamento",
            "pagamentos",
            "taxa",
            "taxas",
            "recebimento",
            "recebimentos",
            "venda",
            "vendas",
            "cartão",
            "cartoes",
            "cartões"
        ]

        message_lower = message.lower()

        return any(
            keyword in message_lower
            for keyword in keywords
        )

    def handle(self, message: str) -> dict:
        """
        Responde utilizando RAG ou busca web.
        """

        if self.is_getnet_question(message):
            return self.handle_rag(message)

        return self.handle_web(message)

    def handle_rag(self, message: str) -> dict:
        """
        Responde utilizando a base RAG da Getnet.
        """

        documents = retriever.search(
            query=message,
            top_k=3
        )

        context = "\n\n".join(
            document["content"]
            for document in documents
        )

        sources = list({
            document["source"]
            for document in documents
        })

        prompt = f"""
Você é um assistente especialista nos produtos
e serviços da Getnet.

Responda utilizando apenas o contexto fornecido.

Não invente informações.

CONTEXTO:
{context}

PERGUNTA:
{message}

RESPOSTA:
"""

        answer = llm_service.generate(prompt)

        return {
            "agent": "knowledge",
            "answer": answer,
            "sources": sources
        }

    def handle_web(self, message: str) -> dict:
        """
        Responde utilizando busca na internet.
        """

        results = search_web(
            query=message,
            max_results=3
        )

        context = "\n\n".join(
            f"Título: {result['title']}\n"
            f"Resumo: {result['snippet']}\n"
            f"URL: {result['url']}"
            for result in results
        )

        sources = [
            result["url"]
            for result in results
        ]

        prompt = f"""
Você é um assistente de conhecimento geral.

Utilize os resultados da busca web abaixo
para responder a pergunta.

Não invente informações.

RESULTADOS DA BUSCA:
{context}

PERGUNTA:
{message}

RESPOSTA:
"""

        answer = llm_service.generate(prompt)

        return {
            "agent": "knowledge",
            "answer": answer,
            "sources": sources
        }


knowledge_agent = KnowledgeAgent()