from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field, field_validator
from .tools import SourceItem


class ChatRequest(BaseModel):
    message: str = Field(min_length=2, max_length=4000)
    user_id: str = Field(min_length=2, max_length=120)

    @field_validator("message", "user_id", mode="before")
    @classmethod
    def strip_values(cls, value: str) -> str:
        if not isinstance(value, str):
            raise ValueError("value must be a string")
        value = value.strip()
        if not value:
            raise ValueError("value must not be blank")
        return value


class ChatResponse(BaseModel):
    request_id: str
    agent: str
    answer: str
    tool: str | None = None
    sources: list[SourceItem] = Field(default_factory=list)
    escalated: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)


class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    rag_index_ready: bool
