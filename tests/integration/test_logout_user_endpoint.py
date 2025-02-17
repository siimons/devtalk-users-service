import pytest
from httpx import AsyncClient
from fastapi import status


@pytest.mark.asyncio
async def test_logout_user_success(auth_client: AsyncClient):
    """
    Тест успешного выхода пользователя из системы.
    Должен вернуть 200 OK и удалить cookies access_token и refresh_token.
    """
    response = await auth_client.post("/api/v1/auth/logout")

    assert response.status_code == status.HTTP_200_OK, f"Ошибка: {response.text}"
    assert response.json() == {"message": "Вы успешно вышли из системы."}

    set_cookie_headers = response.headers.get_list("set-cookie")

    assert any("access_token=" in header and "Max-Age=0" in header for header in set_cookie_headers), \
        "access_token не удалён"

    assert any("refresh_token=" in header and "Max-Age=0" in header for header in set_cookie_headers), \
        "refresh_token не удалён"


@pytest.mark.asyncio
async def test_logout_user_without_auth(client: AsyncClient):
    """
    Тест выхода без аутентификации.
    Должен вернуть 200 OK и отправить заголовки Set-Cookie с пустыми значениями.
    """
    response = await client.post("/api/v1/auth/logout")

    assert response.status_code == status.HTTP_200_OK, f"Ошибка: {response.text}"
    assert response.json() == {"message": "Вы успешно вышли из системы."}

    set_cookie_headers = response.headers.get_list("set-cookie")

    assert any("access_token=" in header and "Max-Age=0" in header for header in set_cookie_headers), \
        "access_token не был очищен"

    assert any("refresh_token=" in header and "Max-Age=0" in header for header in set_cookie_headers), \
        "refresh_token не был очищен"
