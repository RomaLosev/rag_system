from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from fastapi.websockets import WebSocket

from app.ai_model.rag_model import RagModel
from app.dependencies.containers import Container
from app.handlers.chat_handler import ChatRagHandler, ChatRagSimpleHandler
from app.schemas.requests import ChatRequest

chat_router = APIRouter(prefix="/chat", tags=["Chat"])


@chat_router.get(
    "/ws_connect",
    name="WebSocket connection",
    responses={
        "101": {"description": "Switching Protocols"},
        "400": {"description": "Bad Request"},
        "1000": {"description": "Normal Close"},
        "4001": {"description": "Close with error"},
    },
)
async def chat():
    """Documented route for swagger"""
    pass


@chat_router.websocket("/ws_connect", name="Start chat")
@inject
async def chat_with_gemma(
    websocket: WebSocket,
    llm: RagModel = Depends(Provide[Container.rag_model]),
):
    async with ChatRagHandler(websocket=websocket, chat_model=llm) as ws_chat:
        await ws_chat.chat()


@chat_router.post("")
@inject
async def get_answer(
    request: ChatRequest,
    llm: RagModel = Depends(Provide[Container.rag_model]),
):
    handler = ChatRagSimpleHandler(chat_model=llm)
    return await handler.get_answer(message=request.query)
