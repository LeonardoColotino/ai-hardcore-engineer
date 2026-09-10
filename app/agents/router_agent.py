from app.agents.knowledge_agent import knowledge_agent
from app.agents.support_agent import support_agent
from app.services.llm import llm_service


class RouterAgent:

    def classify(self, message: str) -> str:
        prompt = f"""
Você é um roteador de um sistema de atendimento da Getnet.

Classifique a mensagem em apenas uma das opções:

knowledge
support

knowledge:
Perguntas sobre produtos, serviços, regras,
funcionamento, taxas ou informações gerais.

support:
Problemas pessoais do cliente, pagamentos,
vendas, depósitos, máquina com erro,
saldo ou informações da conta.

Responda APENAS com:
knowledge
ou
support

Mensagem:
{message}
"""

        result = llm_service.generate(prompt)

        route = result.strip().lower()

        if "support" in route:
            return "support"

        return "knowledge"

    def handle(self, user_id: str, message: str) -> dict:

        route = self.classify(message)

        if route == "support":
            return support_agent.handle(
                user_id=user_id,
                message=message
            )

        return knowledge_agent.handle(
            message=message
        )


router_agent = RouterAgent()