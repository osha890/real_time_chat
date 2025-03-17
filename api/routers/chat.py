from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException

from api.user_tools import get_current_user_payload, get_token_from_websocket
from api.websocket_manager import manager

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

    try:
        while True:
            data = await websocket.receive_json()
            recipient = data.get("recipient")
            message = data.get("message")
            if message and recipient:
                await manager.send_message(username, recipient, message)
    except WebSocketDisconnect:
        manager.disconnect(username)
