from __future__ import annotations
from dataclasses import dataclass
from app.agents.base import AgentResult


@dataclass
class EscalationAgent:
    def handle(self, message: str, reason: str = "low confidence") -> AgentResult:
        return AgentResult(
            answer="Não consegui resolver esta solicitação com evidência suficiente. Vou encaminhá-la para atendimento humano.",
            tool="human_handoff",
            escalated=True,
            metadata={"handoff_reason": reason, "handoff_status": "pending_persistence", "ticket_created": False},
        )
