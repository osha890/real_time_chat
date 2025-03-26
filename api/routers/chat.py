from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from pymongo.errors import PyMongoError

from api.services.user_service import get_current_user_payload, get_token_from_websocket
from api.services.chat_service import send_undelivered_messages, handle_incoming_message, get_chat_id
from api.services.websocket_manager import manager
from database.crud import get_user_by_username, get_chat_messages_by_chat_id

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


@router.get("/chat/")
async def get_chat_history(recipient: str, payload: dict = Depends(get_current_user_payload)):
    """Получение истории чата"""
    username = payload.get("sub")
    if not await get_user_by_username(recipient):
        raise HTTPException(status_code=404, detail="Recipient not found")
    chat_id = get_chat_id(username, recipient)
    messages = await get_chat_messages_by_chat_id(chat_id)
    message_list_to_response = [  # Формируем ответ
        {
            "sender": msg.get("sender"),
            "message": msg.get("message"),
            "timestamp": msg.get("timestamp")
        }
        for msg in messages
    ]
    return {f"{chat_id}": message_list_to_response}
