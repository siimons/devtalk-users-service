import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_logout_user_success(auth_client: AsyncClient):
    """
    Тест успешного выхода пользователя из системы.
    Должен вернуть 204 No Content и удалить cookies access_token и refresh_token.
    """
    response = await auth_client.post("/api/v1/auth/logout")

    assert response.status_code == status.HTTP_204_NO_CONTENT, f"Ошибка: {response.text}"
    assert response.content == b"", "Ответ должен быть пустым для 204 No Content"

    set_cookie_headers = response.headers.get_list("set-cookie")

    assert any("access_token=" in header and "Max-Age=0" in header for header in set_cookie_headers), \
        f"access_token не удалён, заголовки: {set_cookie_headers}"

    assert any("refresh_token=" in header and "Max-Age=0" in header for header in set_cookie_headers), \
        f"refresh_token не удалён, заголовки: {set_cookie_headers}"


@pytest.mark.asyncio
async def test_logout_user_without_auth(client: AsyncClient):
    """
    Тест выхода без аутентификации.
    Должен вернуть 204 No Content и отправить заголовки Set-Cookie с пустыми значениями.
    """
    response = await client.post("/api/v1/auth/logout")

    assert response.status_code == status.HTTP_204_NO_CONTENT, f"Ошибка: {response.text}"
    assert response.content == b"", "Ответ должен быть пустым для 204 No Content"

    set_cookie_headers = response.headers.get_list("set-cookie")

    assert any("access_token=" in header and "Max-Age=0" in header for header in set_cookie_headers), \
        f"access_token не был очищен, заголовки: {set_cookie_headers}"

    assert any("refresh_token=" in header and "Max-Age=0" in header for header in set_cookie_headers), \
        f"refresh_token не был очищен, заголовки: {set_cookie_headers}"
