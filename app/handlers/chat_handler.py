from fastapi.websockets import WebSocket

from app.ai_model.rag_model import RagModel
from app.common.websocket_manager import WebSocketManager


class ChatRagHandler(WebSocketManager):
    def __init__(self, websocket: WebSocket, chat_model: RagModel):
        super().__init__(websocket=websocket)
        self.bot = chat_model

    async def chat(self):
        await self.ws_send_text("Добрый день! Задайте свой вопрос.")
        while True:
            message = await self.ws_receive_message()
            if message == "/close":
                await self.ws_send_text("Рад был помочь!")
                await self.normal_close()
                break
            answer = await self.bot.get_response(message)
            if answer:
                await self.ws_send_text(answer)


class ChatRagStreamingHandler:
    def __init__(self, chat_model: RagModel):
        self.bot = chat_model

    async def get_answer(self, message: str):
        async for chunk in self.bot.get_stream_response(message):
            yield chunk
