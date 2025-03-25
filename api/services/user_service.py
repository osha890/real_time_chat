from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from typing import Optional

from database.token import verify_token

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_current_user_payload(token: str = Depends(oauth2_scheme)) -> dict:
    """Декодирует токен"""

    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token or expired token")
    return payload


async def get_token_from_websocket(websocket) -> Optional[str]:
    """Достает токен из заголовка websocket"""

    token = websocket.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        return None

    return token.split("Bearer ")[1]