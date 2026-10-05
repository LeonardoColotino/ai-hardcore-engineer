from __future__ import annotations

import re
from dataclasses import dataclass
from app.agents.base import AgentResult
from app.tools.customer_lookup import CustomerLookupTool
from app.tools.transaction_lookup import TransactionLookupTool
from app.tools.payment_status import PaymentStatusTool


@dataclass
class SupportAgent:
    customer_tool: CustomerLookupTool
    transaction_tool: TransactionLookupTool
    payment_tool: PaymentStatusTool

    def handle(self, message: str, user_id: str) -> AgentResult:
        customer = self.customer_tool.run(user_id)
        if not customer.success:
            return AgentResult(
                answer="I could not verify this customer. For privacy, I will not expose account information.",
                tool=self.customer_tool.name,
                escalated=True,
                metadata={"reason": "customer_not_verified"},
            )

        if re.search(r"deposit|settlement|receive|receb|ca[ií]r|dep[oó]sito|pagamento", message, re.I):
            result = self.payment_tool.run(user_id)
            if not result.success:
                return AgentResult(answer="No settlement record was found for this account. Human review is recommended.", tool=self.payment_tool.name, escalated=True, metadata={"reason": "payment_record_unavailable"})
            first = result.data["payments"][0]
            return AgentResult(
                answer=f"Latest settlement status: {first.get('status')}. Expected date: {first.get('expected_date')}. Amount: {first.get('amount')}.",
                tool=self.payment_tool.name,
                metadata={"records": result.data["count"]},
            )

        if re.search(r"transaction|transa[cç][aã]o|declin|recusad|sale|venda", message, re.I):
            result = self.transaction_tool.run(user_id)
            if not result.success:
                return AgentResult(answer="No transaction record was found for this account. Human review is recommended.", tool=self.transaction_tool.name, escalated=True, metadata={"reason": "transaction_record_unavailable"})
            first = result.data["transactions"][0]
            return AgentResult(
                answer=f"Latest transaction: status={first.get('status')}, amount={first.get('amount')}, channel={first.get('channel')}. Reference={first.get('reference')}.",
                tool=self.transaction_tool.name,
                metadata={"records": result.data["count"]},
            )

        if re.search(r"machine|maquin|internet|connect|conecta", message, re.I):
            return AgentResult(
                answer="I verified the customer account. Please restart the terminal, confirm Wi-Fi/mobile-data connectivity, and retry. If the error persists, escalate with the terminal identifier and timestamp; do not send passwords or card data.",
                tool=self.customer_tool.name,
            )

        return AgentResult(
            answer="I verified the customer, but the request is not specific enough for an account action. I will route it for human review.",
            tool=self.customer_tool.name,
            escalated=True,
        )
