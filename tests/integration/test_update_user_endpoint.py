import pytest
from httpx import AsyncClient
from fastapi import status

from app.api.v1.exceptions import (
    InvalidCredentialsException,
    TooManyRequestsException,
)


@pytest.mark.asyncio
async def test_update_user_success(auth_client: AsyncClient):
    """
    Тест успешного обновления данных пользователя.
    Должен вернуть 200 OK и обновлённые данные.
    """
    update_payload = {
        "username": "updateduser",
        "email": "updated@example.com",
        "current_password": "securepassword123"
    }

    response = await auth_client.patch("/api/v1/users/current", json=update_payload)

    assert response.status_code == status.HTTP_200_OK, f"Ошибка: {response.text}"
    response_json = response.json()

    assert response_json["username"] == update_payload["username"], "Имя пользователя не обновилось"
    assert response_json["email"] == update_payload["email"], "Email не обновился"


@pytest.mark.asyncio
async def test_update_user_invalid_password(auth_client: AsyncClient):
    """
    Тест попытки обновления данных с неверным текущим паролем.
    Должен вернуть 401 Unauthorized.
    """
    update_payload = {
        "username": "newuser",
        "email": "new@example.com",
        "current_password": "wrongpassword"
    }

    response = await auth_client.patch("/api/v1/users/current", json=update_payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Ошибка: {response.text}"
    assert response.json()["detail"] == InvalidCredentialsException().message, "Сообщение об ошибке некорректно"


@pytest.mark.asyncio
async def test_update_user_without_password(auth_client: AsyncClient):
    """
    Тест попытки смены email без указания текущего пароля.
    Должен вернуть 401 Unauthorized.
    """
    update_payload = {
        "email": "new@example.com"
    }

    response = await auth_client.patch("/api/v1/users/current", json=update_payload)

    assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Ошибка: {response.text}"
    assert response.json()["detail"] == InvalidCredentialsException().message, "Некорректное сообщение об ошибке"


@pytest.mark.asyncio
async def test_update_user_rate_limit(auth_client: AsyncClient):
    """
    Тест блокировки пользователя после 5 неудачных попыток смены email или пароля.
    Должен вернуть 429 Too Many Requests после 5 попыток.
    """
    update_payload = {
        "email": "new@example.com",
        "current_password": "wrongpassword"
    }

    for attempt in range(5):
        response = await auth_client.patch("/api/v1/users/current", json=update_payload)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Попытка {attempt + 1}: {response.text}"

    response = await auth_client.patch("/api/v1/users/current", json=update_payload)
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS, f"Ошибка: {response.text}"
    assert response.json()["detail"] == TooManyRequestsException(retry_after=1800).message, \
        "Некорректное сообщение об ошибке"


@pytest.mark.asyncio
async def test_update_user_clear_auth_tokens(auth_client: AsyncClient):
    """
    Тест удаления токенов после смены пароля.
    Должен вернуть 200 OK и удалить cookies access_token и refresh_token.
    """
    update_payload = {
        "username": "updateduser",
        "email": "updated@example.com",
        "password": "newsecurepassword123",
        "current_password": "securepassword123"
    }

    response = await auth_client.patch("/api/v1/users/current", json=update_payload)

    assert response.status_code == status.HTTP_200_OK, f"Ошибка: {response.text}"

    set_cookie_headers = response.headers.get_list("set-cookie")

    assert any("access_token=" in header and "Max-Age=0" in header for header in set_cookie_headers), \
        f"access_token не удалён, заголовки: {set_cookie_headers}"

    assert any("refresh_token=" in header and "Max-Age=0" in header for header in set_cookie_headers), \
        f"refresh_token не удалён, заголовки: {set_cookie_headers}"
