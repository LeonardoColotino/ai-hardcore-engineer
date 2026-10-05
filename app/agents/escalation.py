from __future__ import annotations
from dataclasses import dataclass
from app.agents.base import AgentResult


@dataclass
class EscalationAgent:
    def handle(self, message: str, reason: str = "low confidence") -> AgentResult:
        return AgentResult(
            answer="I cannot resolve this request with enough confidence. Human review is recommended; this demo does not create or send a support ticket.",
            tool="human_handoff",
            escalated=True,
            metadata={"handoff_reason": reason, "handoff_status": "recommended", "ticket_created": False},
        )
