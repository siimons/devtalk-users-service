import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_register_user_success(client: AsyncClient, get_test_user_payload):
    """
    Тест успешной регистрации нового пользователя.
    Должен вернуть 201 CREATED и корректные данные пользователя.
    """
    response = await client.post("/api/v1/auth/register", json=get_test_user_payload)

    assert response.status_code == status.HTTP_201_CREATED, f"Ошибка: {response.text}"

    response_data = response.json()
    assert response_data["username"] == get_test_user_payload["username"]
    assert response_data["email"] == get_test_user_payload["email"]
    assert "id" in response_data, "Ответ должен содержать ID пользователя"


@pytest.mark.asyncio
async def test_register_user_duplicate_email(client: AsyncClient, create_test_user):
    """
    Тест: регистрация пользователя с уже существующим email.
    Должен вернуть 400 BAD REQUEST с соответствующим сообщением об ошибке.
    """
    payload = {
        "username": "anotheruser",
        "email": create_test_user["email"],
        "password": "newpassword123",
    }

    response = await client.post("/api/v1/auth/register", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST, f"Ошибка: {response.text}"
    assert response.json() == {
        "detail": f'Пользователь с email "{create_test_user["email"]}" уже существует.'
    }
