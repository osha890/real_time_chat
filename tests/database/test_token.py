import jwt
from datetime import datetime, timedelta, timezone
from database.token import create_access_token, create_refresh_token, verify_token
from config import SECRET_KEY, ALGORITHM

def test_create_access_token(token_data):
    """Проверяет создание access-токена"""
    token = create_access_token(token_data)
    assert isinstance(token, str)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    assert decoded["sub"] == token_data["sub"]
    assert "exp" in decoded
    assert datetime.fromtimestamp(decoded["exp"], timezone.utc) > datetime.now(timezone.utc)

def test_create_refresh_token(token_data):
    """Проверяет создание refresh-токена"""
    token = create_refresh_token(token_data)
    assert isinstance(token, str)

    decoded = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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
    invalid_token = "invalid.token.string"
    decoded = verify_token(invalid_token)
    assert decoded is None  # Токен должен быть недействителен