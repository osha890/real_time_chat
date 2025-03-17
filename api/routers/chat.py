from datetime import datetime, timezone
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException

from api.user_tools import get_current_user_payload, get_token_from_websocket
from api.websocket_manager import manager

from database.crud import save_message_doc, update_message_to_delivered, update_recipients_messages_to_delivered, get_undelivered_messages

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Подключает пользователя к websocket"""

    token = await get_token_from_websocket(websocket)
    user = get_current_user_payload(token)
    username = user.get("sub")
    if not username:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    await manager.connect(username, websocket)

    # Проверяем и помечаем сообщения как "доставленные"
    undelivered_messages = await get_undelivered_messages(username)
    if undelivered_messages:
        for msg in undelivered_messages:
            await websocket.send_json({"sender": msg["sender"], "message": msg["message"]})
        await update_recipients_messages_to_delivered(username)

    try:
        while True:
            data = await websocket.receive_json()
            recipient = data.get("recipient")
            message = data.get("message")

            if not message or not recipient:
                continue

            # Формируем chat_id (например, userA_userB)
            chat_id = "_".join(sorted([username, recipient]))

            # Сохраняем сообщение в MongoDB
            message_doc = {
                "chat_id": chat_id,
                "sender": username,
                "recipient": recipient,
                "message": message,
                "timestamp": datetime.now(timezone.utc),
                "delivered": False  # Изначально сообщение недоставлено
            }

            result = await save_message_doc(message_doc)

            # Отправляем сообщение, если получатель онлайн
            if recipient in manager.active_connections:
                await manager.send_message(username, recipient, message)
                await update_message_to_delivered(result.inserted_id)


    except WebSocketDisconnect:
        manager.disconnect(username)
