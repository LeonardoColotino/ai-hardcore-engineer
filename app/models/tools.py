from __future__ import annotations

from typing import Any
from pydantic import BaseModel, Field


class SourceItem(BaseModel):
    title: str = ""
    url: str = ""
    snippet: str = ""
    score: float | None = None


class ToolResult(BaseModel):
    success: bool
    data: dict[str, Any] = Field(default_factory=dict)
    error: str | None = None
    sources: list[SourceItem] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
