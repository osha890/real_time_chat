from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException

from api.user_tools import get_current_user_payload, get_token_from_websocket
from api.websocket_manager import manager

from database.crud import (
    save_message_doc,
    get_undelivered_messages,
    get_user_by_username,
)

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Работа с websocket"""

    # Подключаем пользователя к websocket
    token = await get_token_from_websocket(websocket)
    user = get_current_user_payload(token)
    username = user.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    await manager.connect(username, websocket)

    # Отправляем неотправленные сообщения
    undelivered_messages = await get_undelivered_messages(username)
    for msg in undelivered_messages:
        await manager.send_message(
            sender=msg.get("sender"),
            recipient=msg.get("recipient"),
            message=msg.get("message"),
            message_doc_id=msg.get("_id")
        )

    try:
        while True:
            data = await websocket.receive_json()
            recipient = data.get("recipient")
            if not recipient:
                await websocket.send_json({"error": "Field 'recipient' is required"})
                continue

            message = data.get("message")
            if not message:
                await websocket.send_json({"error": "Field 'message' is required"})
                continue

            if not await get_user_by_username(recipient):
                await websocket.send_json({"error": "Recipient does not exist"})
                continue

            # Формируем chat_id (например, userA_userB)
            chat_id = "_".join(sorted([username, recipient]))

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

    except WebSocketDisconnect:
        manager.disconnect(username)
