from fastapi import WebSocket
from typing import List


class WebSocketManager:
    """Manages WebSocket connections and broadcasts messages."""
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        """
        Accept a WebSocket connection and add it to the active connections list.
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    async def disconnect(self, websocket: WebSocket):
        """
        Remove a WebSocket connection from the active connections list.
        """
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        """
        Send a message to all active WebSocket connections.
        """
        for connection in self.active_connections:
            await connection.send_text(message)
