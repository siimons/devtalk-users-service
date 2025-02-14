import jwt
from jose.exceptions import JWTError

from fastapi import Request, HTTPException, status, Depends
from datetime import datetime, timezone

from app.api.v1.crud import get_user_by_id
from app.core.dependencies import db
from app.core.config import settings


def get_token(request: Request) -> str:
    """
    Извлекает JWT access-токен из cookie запроса.

    :param request: HTTP-запрос.
    :return: Строка access-токена.
    :raises HTTPException: Если токен отсутствует.
    """
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token not found",
        )
    return token


async def get_current_user(token: str = Depends(get_token)):
    """
    Проверяет валидность JWT access-токена и возвращает данные пользователя.

    :param token: JWT-токен, полученный из cookie.
    :return: Данные пользователя.
    :raises HTTPException: Если токен невалидный, истек, либо пользователь не найден.
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid access token",
        )

    expire = payload.get("exp")
    if not expire or datetime.fromtimestamp(expire, tz=timezone.utc) < datetime.now(timezone.utc):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Access token has expired",
        )

    user_id = payload.get("sub")
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User ID not found in token",
        )

    user = await get_user_by_id(db, int(user_id))
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user