from unittest.mock import patch

from fastapi.testclient import TestClient
from main import app


# Создайте фиктивные данные для теста
mock_user = {"username": "testuser"}
mock_saved_user = {"_id": "mockid", "username": "testuser", "password_hash": "hashed_password"}


# Тестирование маршрута регистрации
@patch('api.routers.auth.save_user')
@patch('api.routers.auth.get_user_by_username')
def test_register(mock_get_user_by_username, mock_save_user):
    # Настроим поведение моков
    mock_get_user_by_username.return_value = None  # Возвращаем None, чтобы пользователь не был найден
    mock_save_user.return_value = mock_saved_user  # Возвращаем данные пользователя после сохранения

    client = TestClient(app)

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


# Тест, когда пользователь уже зарегистрирован
@patch('api.routers.auth.save_user')
@patch('api.routers.auth.get_user_by_username')
def test_register_user_exists(mock_get_user_by_username, mock_save_user):
    # Настроим поведение моков
    mock_get_user_by_username.return_value = mock_user  # Возвращаем None, чтобы пользователь не был найден
    mock_save_user.return_value = mock_saved_user  # Возвращаем данные пользователя после сохранения

    client = TestClient(app)

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
