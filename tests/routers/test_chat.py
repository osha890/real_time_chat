import pytest
from unittest.mock import patch, AsyncMock
from httpx import AsyncClient
from fastapi import status
from fastapi.testclient import TestClient

from api.services.chat_service import get_chat_id
from main import app  # Убедись, что путь правильный
from api.services.user_service import get_current_user_payload

CHAT_MODULE = "api.routers.chat"

client = TestClient(app)


@pytest.fixture
def override_auth():
    """Переопределяет зависимость get_current_user_payload на время теста."""
    app.dependency_overrides[get_current_user_payload] = lambda: {"sub": "test_user"}
    yield
    app.dependency_overrides.pop(get_current_user_payload, None)


@pytest.mark.asyncio
@patch(f"{CHAT_MODULE}.get_user_by_username", new_callable=AsyncMock)
@patch(f"{CHAT_MODULE}.get_chat_messages_by_chat_id", new_callable=AsyncMock)
async def test_get_chat_history_success(mock_get_chat_messages, mock_get_user_by_username, override_auth):
    mock_get_user_by_username.return_value = True
    mock_get_chat_messages.return_value = [
        {"sender": "test_user", "message": "Hello!", "timestamp": "2025-03-25T12:00:00"},
        {"sender": "recipient_user", "message": "Hi!", "timestamp": "2025-03-25T12:01:00"},
    ]

    response = client.get(
        "/chat/",
        params={"recipient": "recipient_user"},
        headers={"Authorization": "Bearer testtoken"}  # Добавляем заголовок (если зависимость требует)
    )

    chat_id = get_chat_id("test_user", "recipient_user")

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        f"{chat_id}": mock_get_chat_messages.return_value
    }


@pytest.mark.asyncio
@patch(f"{CHAT_MODULE}.get_user_by_username", new_callable=AsyncMock)
async def test_get_chat_history_recipient_not_found(mock_get_user_by_username, override_auth):
    mock_get_user_by_username.return_value = None

    response = client.get(
        "/chat/",
        params={"recipient": "unknown_user"},
        headers={"Authorization": "Bearer testtoken"}  # Добавляем заголовок (если зависимость требует)
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json()["detail"] == "Recipient not found"
