from __future__ import annotations

import logging
import time
import uuid
from dataclasses import dataclass
from app.agents.router import RouterAgent
from app.agents.knowledge import KnowledgeAgent
from app.agents.support import SupportAgent
from app.agents.escalation import EscalationAgent
from app.guardrails.guardrails import InputGuardrails
from app.models.api import ChatRequest, ChatResponse
from app.models.routing import AgentName
from app.observability.logging import log_event

logger = logging.getLogger(__name__)


@dataclass
class Orchestrator:
    router: RouterAgent
    knowledge: KnowledgeAgent
    support: SupportAgent
    escalation: EscalationAgent
    guardrails: InputGuardrails

    def handle(self, request: ChatRequest) -> ChatResponse:
        started = time.perf_counter()
        request_id = f"req-{uuid.uuid4().hex[:12]}"
        previous_agent = None
        previous_tool = None
        handoff_reason = None
        guard = self.guardrails.check(request.message)
        if not guard.allowed:
            result = self.escalation.handle(request.message, guard.reason)
            decision_agent = AgentName.ESCALATION
            confidence = 1.0
            route_reason = guard.reason
        else:
            decision = self.router.route(request.message)
            decision_agent = decision.agent
            confidence = decision.confidence
            route_reason = decision.reason
            if decision.agent == AgentName.KNOWLEDGE:
                result = self.knowledge.handle(request.message)
            elif decision.agent == AgentName.SUPPORT:
                result = self.support.handle(request.message, request.user_id)
            else:
                result = self.escalation.handle(request.message, decision.reason)

            if result.escalated and decision.agent != AgentName.ESCALATION:
                previous_agent = decision.agent.value
                previous_tool = result.tool
                handoff_reason = result.metadata.get("fallback") or result.metadata.get("reason") or "specialized_agent_fallback"
                handoff = self.escalation.handle(request.message, handoff_reason)
                handoff.metadata["previous_agent"] = previous_agent
                handoff.metadata["previous_tool"] = previous_tool
                result = handoff
                decision_agent = AgentName.ESCALATION

        duration_ms = round((time.perf_counter() - started) * 1000, 2)
        log_event(
            logger,
            "request_completed",
            request_id=request_id,
            agent=decision_agent.value,
            tool=result.tool,
            duration_ms=duration_ms,
            success=True,
            resolved=not result.escalated,
            previous_agent=previous_agent,
            previous_tool=previous_tool,
            handoff_reason=result.metadata.get("handoff_reason"),
            routing_reason=route_reason,
            escalated=result.escalated,
            routing_confidence=confidence,
        )
        return ChatResponse(
            request_id=request_id,
            agent=decision_agent.value,
            answer=result.answer,
            tool=result.tool,
            sources=result.sources,
            escalated=result.escalated,
            metadata={"duration_ms": duration_ms, "routing_confidence": round(confidence, 3), "routing_reason": route_reason, **result.metadata},
        )
