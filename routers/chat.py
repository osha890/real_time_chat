from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from websocket_manager import manager
from database.crud import get_user_by_username

router = APIRouter()


@router.websocket("/ws/{username}")
async def websocket_endpoint(username: str, websocket: WebSocket):
    user = await get_user_by_username(username)
    if not user:
        await websocket.close(code=1008)  # Закрываем соединение
        return

    await manager.connect(username, websocket)

    try:
        while True:
            data = await websocket.receive_json()
            await manager.send_message(username, data["message"])
    except WebSocketDisconnect:
        manager.disconnect(username)
