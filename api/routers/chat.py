from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from pymongo.errors import PyMongoError

from api.services.user_service import get_current_user_payload, get_token_from_websocket
from api.services.chat_service import send_undelivered_messages, handle_incoming_message
from api.services.websocket_manager import manager

router = APIRouter()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Работа с websocket"""

    # Подключаем пользователя к websocket
    try:
        token = await get_token_from_websocket(websocket)
        user = get_current_user_payload(token)
        username = user.get("sub")
        if not username:
            raise ValueError("Missing username in token payload")
    except (ValueError, AttributeError):
        await websocket.close(code=1008)
        return

    await manager.connect(username, websocket)

    # Отправляем неотправленные сообщения
    try:
        await send_undelivered_messages(username)
    except PyMongoError as e:
        await websocket.send_json({"error": f"Database error: {str(e)}"})
        await websocket.close(code=1011)
        return

    try:
        while True:
            try:
                await handle_incoming_message(websocket, username)
            except PyMongoError as e:
                await websocket.send_json({"error": f"Database error: {str(e)}"})
                break  # Выход из цикла при ошибке БД
            except WebSocketDisconnect:
                break  # Выход при отключении клиента
    finally:
        manager.disconnect(username)  # Очистка соединения
