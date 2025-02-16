import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_get_current_user_success(client: AsyncClient, create_test_user, get_test_user_payload):
    """
    Тест успешного получения данных текущего пользователя.
    Должен вернуть 200 OK и корректные данные.
    """
    login_payload = {
        "email": get_test_user_payload["email"],
        "password": get_test_user_payload["password"],
    }
    login_response = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_response.status_code == status.HTTP_200_OK, f"Ошибка: {login_response.text}"

    login_data = login_response.json()
    access_token = login_data["access_token"]
    assert access_token, "В ответе должен быть access_token"

    response = await client.get("/api/v1/users/current", headers={"Authorization": f"Bearer {access_token}"})
    
    assert response.status_code == status.HTTP_200_OK, f"Ошибка: {response.text}"
    
    response_data = response.json()
    assert response_data["id"] == create_test_user["id"]
    assert response_data["username"] == create_test_user["username"]
    assert response_data["email"] == create_test_user["email"]


@pytest.mark.asyncio
async def test_get_current_user_unauthorized(client: AsyncClient):
    """
    Тест получения текущего пользователя без авторизации.
    Должен вернуть 401 Unauthorized.
    """
    response = await client.get("/api/v1/users/current")

    assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Ошибка: {response.text}"
