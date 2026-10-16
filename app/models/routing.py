from __future__ import annotations

from enum import Enum
from pydantic import BaseModel, Field


class AgentName(str, Enum):
    KNOWLEDGE = "knowledge"
    SUPPORT = "support"
    ESCALATION = "escalation"


class RoutingDecision(BaseModel):
    agent: AgentName
    reason: str = Field(min_length=3, max_length=400)
    confidence: float = Field(ge=0.0, le=1.0)
    source: str = "deterministic"
