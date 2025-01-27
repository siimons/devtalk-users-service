import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_get_user_success(client: AsyncClient, create_test_user):
    """
    Тест успешного получения данных пользователя по ID.
    """
    user_id = create_test_user["id"]
    response = await client.get(f"/api/v1/users/{user_id}")

    assert response.status_code == status.HTTP_200_OK
    response_data = response.json()
    assert response_data["id"] == user_id
    assert response_data["username"] == create_test_user["username"]
    assert response_data["email"] == create_test_user["email"]


@pytest.mark.asyncio
async def test_get_user_not_found(client: AsyncClient):
    """
    Тест получения несуществующего пользователя.
    """
    response = await client.get("/api/v1/users/101")
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {"detail": "Пользователь с ID 101 не найден."}