import pytest
from unittest import mock
from database.crud import get_user_by_username
from database.db_conf import user_collection


@pytest.mark.asyncio
async def test_get_user_by_username_found():
    mock_user = {"username": "testuser", "email": "testuser@example.com"}

    # Мокаем коллекцию и метод find_one
    with mock.patch("database.db_conf.user_collection.find_one", new_callable=mock.AsyncMock, return_value=mock_user):
        result = await get_user_by_username("testuser")

        assert result == mock_user
        # Проверим, что поиск по username был вызван
        user_collection.find_one.assert_called_once_with({"username": "testuser"})


@pytest.mark.asyncio
async def test_get_user_by_username_not_found():
    # Мокаем коллекцию и метод find_one для случая, когда пользователя нет
    with mock.patch("database.db_conf.user_collection.find_one", new_callable=mock.AsyncMock, return_value=None):
        result = await get_user_by_username("nonexistentuser")

        assert result is None
        # Проверим, что метод был вызван с правильным параметром
        user_collection.find_one.assert_called_once_with({"username": "nonexistentuser"})

