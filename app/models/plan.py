"""Untrusted planner output cannot contain identity or grant permissions."""
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator

class Task(BaseModel):
    model_config = ConfigDict(extra='forbid')
    agent: Literal['knowledge', 'support', 'escalation']
    query: str = Field(min_length=2, max_length=4000)
    depends_on: int | None = Field(default=None, ge=0)

class Plan(BaseModel):
    model_config = ConfigDict(extra='forbid')
    tasks: list[Task] = Field(min_length=1, max_length=4)
    @model_validator(mode='after')
    def dependencies(self):
        for i, task in enumerate(self.tasks):
            if task.depends_on is not None and task.depends_on >= i:
                raise ValueError('Dependencies must point to earlier tasks')
        return self

class TaskOutcome(BaseModel):
    task_id: int
    agent: str
    status: Literal['accepted', 'unresolved', 'failed', 'blocked']
    tool: str | None = None
    duration_ms: float = 0
    review: str

class TurnState(BaseModel):
    original_message: str
    trusted_user_id: str
    session_id: str = ''
    plan: Plan
    outcomes: list[TaskOutcome] = Field(default_factory=list)
    max_steps: int = 4
    steps_used: int = 0
