from __future__ import annotations

import re
from dataclasses import dataclass
from app.agents.base import AgentResult
from app.tools.customer_lookup import CustomerLookupTool
from app.tools.transaction_lookup import TransactionLookupTool
from app.tools.payment_status import PaymentStatusTool
from app.tools.terminal_diagnosis import TerminalDiagnosisTool, public_diagnosis


@dataclass
class SupportAgent:
    customer_tool: CustomerLookupTool
    transaction_tool: TransactionLookupTool
    payment_tool: PaymentStatusTool

    def handle(self, message: str, user_id: str) -> AgentResult:
        customer = self.customer_tool.run(user_id)
        if not customer.success:
            return AgentResult(
                answer="Não consegui verificar este cliente. Por privacidade, não exibirei informações da conta.",
                tool=self.customer_tool.name,
                escalated=True,
                metadata={"reason": "customer_not_verified"},
            )

        if __import__("app.orchestration.intents", fromlist=["settlement"]).settlement(message):
            result = self.payment_tool.run(user_id)
            if not result.success:
                return AgentResult(answer="Não encontrei registro de pagamento para esta conta. Atendimento humano recomendado.", tool=self.payment_tool.name, escalated=True, metadata={"reason": "payment_record_unavailable"})
            first = result.data["payments"][0]
            return AgentResult(
                answer=f"Status do último pagamento: {first.get('status')}. Data prevista no registro de demonstração: {first.get('expected_date')}. Valor: {first.get('amount')}.",
                tool=self.payment_tool.name,
                metadata={"records": result.data["count"]},
            )

        if re.search(r"transaction|transa[cç][aã]o|declin|recusad|sale|venda", message, re.I):
            result = self.transaction_tool.run(user_id)
            if not result.success:
                return AgentResult(answer="Não encontrei transação para esta conta. Atendimento humano recomendado.", tool=self.transaction_tool.name, escalated=True, metadata={"reason": "transaction_record_unavailable"})
            first = result.data["transactions"][0]
            return AgentResult(
                answer=f"Última transação demonstrativa (registro fixo): status={first.get('status')}, valor={first.get('amount')}, canal={first.get('channel')}. Referência={first.get('reference')}.",
                tool=self.transaction_tool.name,
                metadata={"records": result.data["count"]},
            )

        if re.search(r"machine|maquin|terminal|internet|connect|conecta", message, re.I):
            tool = TerminalDiagnosisTool(self.customer_tool.repository)
            diagnosis = tool.run(user_id)
            if not diagnosis.success:
                return AgentResult(answer="Diagnóstico demonstrativo indisponível.", tool=tool.name, escalated=True)
            public_query = public_diagnosis(diagnosis.data)
            return AgentResult(
                answer="Diagnóstico demonstrativo (telemetria sintética fixa): conexão Wi-Fi indisponível no terminal. Não representa leitura ao vivo da sua maquininha.",
                tool=tool.name,
                metadata={"synthetic": True, "public_diagnosis": public_query, "diagnostic_code": diagnosis.data['diagnostic_code']},
            )

        return AgentResult(
            answer="Cliente verificado, mas preciso de uma solicitação mais específica. Encaminharei para atendimento humano.",
            tool=self.customer_tool.name,
            escalated=True,
        )
