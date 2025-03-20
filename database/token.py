import jwt
from datetime import datetime, timedelta, timezone
from config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS


def create_token(data: dict, time: timedelta):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + time
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_access_token(data: dict):
    """Создание access-токена (действителен ACCESS_TOKEN_EXPIRE_MINUTES минут)"""

    return create_token(data, timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))


def create_refresh_token(data: dict):
    """Создание refresh-токена (действителен REFRESH_TOKEN_EXPIRE_DAYS дней)"""

    return create_token(data, timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS))


def verify_token(token: str):
    """Проверка токена"""

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Токен истек
    except jwt.InvalidTokenError:
        return None  # Неверный токен
