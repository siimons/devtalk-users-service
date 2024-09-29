import sys
import os
import pytest
from fastapi.testclient import TestClient

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app

client = TestClient(app)

@pytest.fixture(scope="module")
def test_user():
    """Возвращает данные для тестового пользователя."""
    return {
        'username': 'Finn',
        'email': 'adventuretime@yandex.ru',
        'password': 'gfdsaqz'
    }

def test_register_user(test_user):
    """Тест на регистрацию нового пользователя."""
    response = client.post('/api/auth/register/', json=test_user)
    
    # Проверяем статус ответа
    assert response.status_code == 200, "Пользователь не был успешно зарегистрирован."
    
    # Проверяем, что ответ содержит корректные данные
    response_data = response.json()
    assert "id" in response_data, "ID пользователя не возвращен."
    assert response_data["username"] == test_user["username"], "Имя пользователя не совпадает."
    assert response_data["email"] == test_user["email"], "Email пользователя не совпадает."

def test_register_user_already_exists(test_user):
    """Тест на регистрацию пользователя с уже существующим email."""
    # Попытка зарегистрировать пользователя с теми же данными
    response = client.post('/api/auth/register/', json=test_user)
    
    # Ожидаем, что статус будет 400, так как пользователь уже существует
    assert response.status_code == 400, "Ожидается ошибка при повторной регистрации пользователя."
    assert "detail" in response.json(), "Нет сообщения об ошибке."

def test_register_user_invalid_email():
    """Тест на регистрацию пользователя с некорректным email."""
    invalid_user = {
        'username': 'Finn',
        'email': 'invalid_email',
        'password': 'gfdsaqz'
    }
    response = client.post('/api/auth/register/', json=invalid_user)
    
    # Ожидаем, что статус будет 400, так как email некорректен
    assert response.status_code == 400, "Ожидается ошибка при регистрации с некорректным email."
    assert "detail" in response.json(), "Нет сообщения об ошибке."

def test_register_user_missing_fields():
    """Тест на регистрацию пользователя без обязательных полей."""
    incomplete_user = {
        'username': 'Finn'
        # Отсутствуют email и password
    }
    response = client.post('/api/auth/register/', json=incomplete_user)

    # Ожидаем, что статус будет 422, так как отсутствуют обязательные поля
    assert response.status_code == 422, "Ожидается ошибка при регистрации без обязательных полей."
    assert "detail" in response.json(), "Нет сообщения об ошибке."
