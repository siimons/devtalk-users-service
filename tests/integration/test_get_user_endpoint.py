import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_get_current_user_success(auth_client: AsyncClient, create_test_user):
    """
    Тест успешного получения данных текущего пользователя.
    Должен вернуть 200 OK и корректные данные.
    """
    response = await auth_client.get("/api/v1/users/current")

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
