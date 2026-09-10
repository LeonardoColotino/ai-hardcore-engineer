
from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    """Representa uma mensagem enviada para o sistema multiagente."""

    message: str = Field(
        ...,
        min_length=1,
        description="Mensagem enviada pelo usuário."
    )

    user_id: str = Field(
        ...,
        min_length=1,
        description="Identificador do usuário."
    )