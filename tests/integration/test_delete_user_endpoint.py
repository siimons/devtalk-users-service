import pytest
from httpx import AsyncClient
from fastapi import status

from app.api.v1.exceptions import (
    InvalidCredentialsException,
    TooManyRequestsException,
)


@pytest.mark.asyncio
async def test_delete_user_success(auth_client: AsyncClient, create_test_user, get_test_user_payload):
    """
    Тест успешного удаления пользователя.
    Должен вернуть 200 OK и сообщение об успешном удалении.
    """
    delete_payload = {"current_password": get_test_user_payload["password"]}

    response = await auth_client.request(
        method="DELETE",
        url="/api/v1/users/current",
        json=delete_payload,
    )

    assert response.status_code == status.HTTP_200_OK, f"Ошибка: {response.text}"
    assert response.json() == {
        "message": "Your account has been successfully deleted. Check your email for restoration instructions."
    }, "Некорректное сообщение об успешном удалении"


@pytest.mark.asyncio
async def test_delete_user_invalid_password(auth_client: AsyncClient):
    """
    Тест попытки удаления пользователя с неверным паролем.
    Должен вернуть 401 Unauthorized.
    """
    delete_payload = {"current_password": "wrongpassword"}

    response = await auth_client.request(
        method="DELETE",
        url="/api/v1/users/current",
        json=delete_payload,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Ошибка: {response.text}"
    assert response.json()["detail"] == InvalidCredentialsException().message, "Некорректное сообщение об ошибке"


@pytest.mark.asyncio
async def test_delete_user_unauthenticated(client: AsyncClient, create_test_user, get_test_user_payload):
    """
    Тест попытки удаления пользователя без авторизации.
    Должен вернуть 401 Unauthorized.
    """
    delete_payload = {"current_password": get_test_user_payload["password"]}

    response = await client.request(
        method="DELETE",
        url="/api/v1/users/current",
        json=delete_payload,
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Ошибка: {response.text}"


@pytest.mark.asyncio
async def test_delete_user_rate_limit(auth_client: AsyncClient):
    """
    Тест блокировки пользователя после 5 неудачных попыток удаления.
    Должен вернуть 429 Too Many Requests после 5 попыток.
    """
    delete_payload = {"current_password": "wrongpassword"}

    for attempt in range(5):
        response = await auth_client.request(
            method="DELETE",
            url="/api/v1/users/current",
            json=delete_payload,
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED, f"Попытка {attempt + 1}: {response.text}"

    response = await auth_client.request(
        method="DELETE",
        url="/api/v1/users/current",
        json=delete_payload,
    )
    assert response.status_code == status.HTTP_429_TOO_MANY_REQUESTS, f"Ошибка: {response.text}"
    assert response.json()["detail"] == TooManyRequestsException(retry_after=1800).message, \
        "Некорректное сообщение об ошибке"
    assert "Retry-After" in response.headers, "Отсутствует заголовок Retry-After"


@pytest.mark.asyncio
async def test_delete_user_clear_auth_tokens(auth_client: AsyncClient, create_test_user, get_test_user_payload):
    """
    Тест удаления токенов после успешного удаления пользователя.
    Должен вернуть 200 OK и удалить cookies access_token и refresh_token.
    """
    delete_payload = {"current_password": get_test_user_payload["password"]}

    response = await auth_client.request(
        method="DELETE",
        url="/api/v1/users/current",
        json=delete_payload,
    )

    assert response.status_code == status.HTTP_200_OK, f"Ошибка: {response.text}"

    set_cookie_headers = response.headers.get_list("set-cookie")

    assert any("access_token=" in header and "Max-Age=0" in header for header in set_cookie_headers), \
        f"access_token не удалён, заголовки: {set_cookie_headers}"

    assert any("refresh_token=" in header and "Max-Age=0" in header for header in set_cookie_headers), \
        f"refresh_token не удалён, заголовки: {set_cookie_headers}"
