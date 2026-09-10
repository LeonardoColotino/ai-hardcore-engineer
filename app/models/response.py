
from pydantic import BaseModel


class ChatResponse(BaseModel):
    """Representa a resposta final do sistema multiagente."""

    agent: str
    answer: str