"""
Aplicação principal FastAPI.

Responsabilidades:
- Inicializar a aplicação
- Inicializar o banco SQLite
- Expor os endpoints HTTP
- Encaminhar mensagens para o Router Agent
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.agents.router_agent import router_agent
from app.config import settings
from app.models.request import ChatRequest
from app.models.response import ChatResponse
from app.tools.payment_tool import initialize_payments
from app.tools.user_database import initialize_database


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Executa tarefas necessárias na inicialização da aplicação.
    """

    initialize_database()
    initialize_payments()

    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan
)


@app.get("/")
def health():
    """
    Verifica se a API está funcionando.
    """

    return {
        "status": "running",
        "application": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


@app.post(
    "/chat",
    response_model=ChatResponse
)
def chat(request: ChatRequest):
    """
    Recebe uma mensagem e envia para o Router Agent.
    """

    result = router_agent.handle(
        user_id=request.user_id,
        message=request.message
    )

    return ChatResponse(**result)