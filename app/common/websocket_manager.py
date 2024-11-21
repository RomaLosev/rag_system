from typing import Self

from fastapi.websockets import WebSocket, WebSocketState


class WebSocketManager:
    def __init__(self, websocket: WebSocket) -> None:
        self.websocket = websocket

    async def __aenter__(self) -> Self:
        await self.websocket.accept()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.normal_close()

    async def ws_send_text(self, message: str) -> None:
        await self.websocket.send_text(message)

    async def ws_receive_message(self) -> str:
        return await self.websocket.receive_text()

    async def close_with_error(self, error_message: str) -> None:
        await self.websocket.close(code=4001, reason=error_message)

    async def normal_close(self) -> None:
        if self.websocket.client_state == WebSocketState.CONNECTED:
            await self.websocket.close()
