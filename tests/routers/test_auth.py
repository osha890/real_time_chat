import pytest

from unittest.mock import patch, AsyncMock, Mock
from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

AUTH_MODULE = "api.routers.auth"

# Создайте фиктивные данные для теста
mock_user = {"username": "testuser"}
mock_db_user = {"username": "testuser", "password_hash": "hashed_password"}
mock_saved_user = {"_id": "mockid", "username": "testuser", "password_hash": "hashed_password"}



# ========================== /register/ test ==========================

@patch(f"{AUTH_MODULE}.save_user")
@patch(f"{AUTH_MODULE}.get_user_by_username")
def test_register(mock_get_user_by_username, mock_save_user):
    # Настроим поведение моков
    mock_get_user_by_username.return_value = None  # Возвращаем None, чтобы пользователь не был найден
    mock_save_user.return_value = mock_saved_user  # Возвращаем данные пользователя после сохранения

    # Параметры для теста
    user_data = {"username": "testuser", "password": "testpassword"}

    # Отправляем запрос на регистрацию
    response = client.post("/register/", json=user_data)

    # Проверяем успешный статус и возвращаемые данные
    assert response.status_code == 200
    assert response.json().get("username") == mock_saved_user.get("username")

    # Проверяем, что моки были вызваны
    mock_get_user_by_username.assert_called_once_with("testuser")
    mock_save_user.assert_called_once()



@patch(f"{AUTH_MODULE}.save_user")
@patch(f"{AUTH_MODULE}.get_user_by_username")
def test_register_user_exists(mock_get_user_by_username, mock_save_user):
    # Настроим поведение моков
    mock_get_user_by_username.return_value = mock_user  # Возвращаем None, чтобы пользователь не был найден
    mock_save_user.return_value = mock_saved_user  # Возвращаем данные пользователя после сохранения

    # Параметры для теста
    user_data = {"username": "testuser", "password": "testpassword"}

    # Отправляем запрос на регистрацию
    response = client.post("/register/", json=user_data)

    # Проверяем успешный статус и возвращаемые данные
    assert response.status_code == 400
    assert response.json().get("detail") == "Username already registered"

    # Проверяем, что моки были вызваны
    mock_get_user_by_username.assert_called_once_with("testuser")
    mock_save_user.assert_not_called()


# ========================== /token/ test ==========================

@pytest.mark.asyncio
@patch(f"{AUTH_MODULE}.verify_password", new_callable=Mock)
@patch(f"{AUTH_MODULE}.get_user_by_username", new_callable=AsyncMock)
@patch(f"{AUTH_MODULE}.save_refresh_token", new_callable=AsyncMock)
async def test_login_success(mock_save_refresh_token, mock_get_user_by_username, mock_verify_password):
    mock_get_user_by_username.return_value = mock_db_user
    mock_verify_password.return_value = True

    response = client.post("/token/", json={"username": "testuser", "password": "password"})

    assert response.status_code == 200
    json_data = response.json()
    assert "access_token" in json_data
    assert "refresh_token" in json_data
    mock_save_refresh_token.assert_called_once()


@pytest.mark.asyncio
@patch(f"{AUTH_MODULE}.verify_password", new_callable=Mock)
@patch(f"{AUTH_MODULE}.get_user_by_username", new_callable=AsyncMock)
@patch(f"{AUTH_MODULE}.save_refresh_token", new_callable=AsyncMock)
async def test_login_no_user(mock_save_refresh_token, mock_get_user_by_username, mock_verify_password):
    mock_get_user_by_username.return_value = None
    mock_verify_password.return_value = True

    response = client.post("/token/", json={"username": "testuser", "password": "password"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


@pytest.mark.asyncio
@patch(f"{AUTH_MODULE}.verify_password", new_callable=Mock)
@patch(f"{AUTH_MODULE}.get_user_by_username", new_callable=AsyncMock)
async def test_login_invalid_credentials(mock_get_user_by_username, mock_verify_password):
    mock_get_user_by_username.return_value = mock_db_user
    mock_verify_password.return_value = False

    response = client.post("/token/", json={"username": "testuser", "password": "wrongpass"})
    print(response.json())

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
