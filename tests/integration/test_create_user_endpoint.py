import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_create_user_success(client: AsyncClient):
    """
    Тест успешного создания пользователя.
    """
    payload = {
        "username": "testuser",
        "email": "testuser@example.com",
        "password": "securepassword123",
    }
    response = await client.post("/api/v1/users", json=payload)

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data["username"] == payload["username"]
    assert response_data["email"] == payload["email"]
    assert "id" in response_data


@pytest.mark.asyncio
async def test_create_user_duplicate_email(client: AsyncClient, create_test_user):
    """
    Тест попытки создать пользователя с уже существующим email.
    """
    payload = {
        "username": "newuser",
        "email": create_test_user["email"],
        "password": "newpassword123",
    }
    response = await client.post("/api/v1/users", json=payload)

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json() == {"detail": f'Пользователь с email "{create_test_user["email"]}" уже существует.'}