from typing import Dict
from fastapi import WebSocket
from database.crud import update_message_to_delivered


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, username: str, websocket: WebSocket):
        await websocket.accept()
        self.active_connections[username] = websocket

    def disconnect(self, username: str):
        self.active_connections.pop(username, None)

    async def send_message(self, sender: str, recipient: str, message: str, message_doc_id: str):
        ws = self.active_connections.get(recipient)
        if ws:
            await ws.send_json({"sender": sender, "message": message})
            await update_message_to_delivered(message_doc_id)


manager = ConnectionManager()
