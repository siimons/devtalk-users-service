import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_login_user_success(client: AsyncClient, create_test_user, get_test_user_payload):
    """
    Тест успешного входа в систему.
    Должен вернуть 200 OK, содержать access_token в ответе и установить cookies.
    """
    payload = {
        "email": get_test_user_payload["email"],
        "password": get_test_user_payload["password"],
    }

    response = await client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == status.HTTP_200_OK, f"Ошибка: {response.text}"

    response_data = response.json()
    assert "access_token" in response_data, "Ответ должен содержать access_token"
    assert response_data["token_type"] == "bearer", "Неверный тип токена"

    access_token_cookie = response.cookies.get("access_token")
    assert access_token_cookie, "access_token должен быть установлен в cookies"

    refresh_token_cookie = response.cookies.get("refresh_token")
    assert refresh_token_cookie, "refresh_token должен быть установлен в cookies"


@pytest.mark.asyncio
async def test_login_user_wrong_password(client: AsyncClient, create_test_user):
    """
    Тест: вход с неправильным паролем.
    Должен вернуть 401 Unauthorized.
    """
    payload = {
        "email": create_test_user["email"],
        "password": "wrongpassword123",
    }

    response = await client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Ошибка: {response.text}"

    response_data = response.json()
    assert response_data["detail"] == "Неверный email или пароль.", "Некорректное сообщение об ошибке"


@pytest.mark.asyncio
async def test_login_user_nonexistent_email(client: AsyncClient):
    """
    Тест: вход с несуществующим email.
    Должен вернуть 401 Unauthorized.
    """
    payload = {
        "email": "nonexistent@example.com",
        "password": "password123",
    }

    response = await client.post("/api/v1/auth/login", json=payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Ошибка: {response.text}"

    response_data = response.json()
    assert response_data["detail"] == "Неверный email или пароль.", "Некорректное сообщение об ошибке"


@pytest.mark.asyncio
async def test_login_user_empty_payload(client: AsyncClient):
    """
    Тест: вход с пустым запросом.
    Должен вернуть 422 Unprocessable Entity.
    """
    response = await client.post("/api/v1/auth/login", json={})

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, f"Ошибка: {response.text}"
