import pytest

@pytest.fixture
def token_data():
    """Тестовые данные для токена"""
    return {"sub": "testuser"}