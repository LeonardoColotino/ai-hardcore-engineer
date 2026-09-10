"""
Agente responsável pelo atendimento ao cliente.
"""

from app.services.llm import llm_service
from app.tools.payment_tool import get_payments
from app.tools.user_database import get_customer


class SupportAgent:
    """Agente especializado em suporte ao cliente."""

    def handle(
        self,
        user_id: str,
        message: str
    ) -> dict:
        """
        Consulta dados do usuário e pagamentos
        antes de gerar a resposta.
        """

        customer = get_customer(user_id)

        if customer is None:
            return {
                "agent": "support",
                "answer": "Cliente não encontrado."
            }

        payments = get_payments(user_id)

        prompt = f"""
Você é um agente de atendimento ao cliente da Getnet.

Utilize apenas os dados abaixo para responder.

Não invente informações sobre o cliente.

DADOS DO CLIENTE:
{customer}

PAGAMENTOS:
{payments}

PERGUNTA DO CLIENTE:
{message}

Responda de forma clara, curta e objetiva.

RESPOSTA:
"""

        answer = llm_service.generate(prompt)

        return {
            "agent": "support",
            "answer": answer
        }


support_agent = SupportAgent()