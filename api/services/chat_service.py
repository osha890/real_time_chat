from datetime import datetime, timezone
from fastapi import WebSocket

from api.services.websocket_manager import manager
from database.crud import get_undelivered_messages, get_user_by_username, save_message_doc


async def send_undelivered_messages(username: str):
    undelivered_messages = await get_undelivered_messages(username)
    for msg in undelivered_messages:
        await manager.send_message(
            sender=msg.get("sender"),
            recipient=msg.get("recipient"),
            message=msg.get("message"),
            message_doc_id=msg.get("_id")
        )


async def handle_incoming_message(websocket: WebSocket, username: str):
    data = await websocket.receive_json()
    recipient = data.get("recipient")
    if not recipient:
        await websocket.send_json({"error": "Field 'recipient' is required"})
        return

    message = data.get("message")
    if not message:
        await websocket.send_json({"error": "Field 'message' is required"})
        return

    if not await get_user_by_username(recipient):
        await websocket.send_json({"error": "Recipient does not exist"})
        return

    chat_id = get_chat_id(username, recipient)

    # Создаем сообщение
    message_doc = {
        "chat_id": chat_id,
        "sender": username,
        "recipient": recipient,
        "message": message,
        "timestamp": datetime.now(timezone.utc),
        "delivered": False
    }

    # Сохраняем сообщение в MongoDB
    result = await save_message_doc(message_doc)

    # Отправляем сообщение, если получатель онлайн
    if recipient in manager.active_connections:
        await manager.send_message(
            sender=username,
            recipient=recipient,
            message=message,
            message_doc_id=result.inserted_id
        )


def get_chat_id(username: str, recipient: str) -> str:
    """Формирует chat_id (например, userA_userB)"""
    return "_".join(sorted([username, recipient]))
