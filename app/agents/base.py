from __future__ import annotations
from dataclasses import dataclass, field
from app.models.tools import SourceItem


@dataclass
class AgentResult:
    answer: str
    tool: str | None = None
    sources: list[SourceItem] = field(default_factory=list)
    escalated: bool = False
    metadata: dict = field(default_factory=dict)
