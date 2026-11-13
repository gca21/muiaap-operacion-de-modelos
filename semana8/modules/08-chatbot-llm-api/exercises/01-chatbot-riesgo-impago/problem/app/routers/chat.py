from typing import Annotated

from fastapi import APIRouter, Depends

from app.schemas.chat import ChatEntrada, ChatSalida
from app.services.llm import LLMLiteLLM, LLMSimulado, get_llm
from app.services.orquestador import responder

router = APIRouter()


# POST /chat (entrada ChatEntrada, salida ChatSalida). Recibe el LLM con Depends(get_llm)
@router.post("/chat", response_model=ChatSalida)
def chat(
    entrada: ChatEntrada,
    llm: Annotated[LLMSimulado | LLMLiteLLM, Depends(get_llm)],
) -> ChatSalida:
    return responder(entrada.mensajes, llm)