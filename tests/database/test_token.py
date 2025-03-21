import jwt
from datetime import datetime, timedelta, timezone
from database.token import create_access_token, create_token, verify_token
from config import SECRET_KEY, ALGORITHM


def test_create_token(token_data):
    """Проверяет создание произвольного токена с разным временем жизни"""
    expire_time = timedelta(hours=1)
    token = create_token(token_data, expire_time)
    assert isinstance(token, str)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded != token_data
    assert decoded["sub"] == token_data["sub"]
    assert "exp" in decoded
    assert datetime.fromtimestamp(decoded["exp"], timezone.utc) > datetime.now(timezone.utc)


def test_verify_valid_token(token_data):
    """Проверяет валидацию валидного токена"""
    token = create_access_token(token_data)
    decoded = verify_token(token)
    assert decoded is not None
    assert decoded["sub"] == token_data["sub"]


def test_verify_expired_token(token_data):
    """Проверяет обработку истекшего токена"""
    expired_time = datetime.now(timezone.utc) - timedelta(minutes=1)
    token = jwt.encode({**token_data, "exp": expired_time}, SECRET_KEY, algorithm=ALGORITHM)

    decoded = verify_token(token)
    assert decoded is None  # Токен должен быть недействителен


def test_verify_invalid_token():
    """Проверяет обработку неверного токена"""
    invalid_token = "qwe123"
    decoded = verify_token(invalid_token)
    assert decoded is None  # Токен должен быть недействителен
