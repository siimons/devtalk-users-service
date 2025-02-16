import jwt
from datetime import datetime, timedelta, timezone
from typing import Optional

from app.core.config import settings


def create_access_token(data: dict, expires_delta: Optional[int] = None) -> str:
    """
    Создает JWT access-токен.

    :param data: Данные, которые будут зашифрованы в токене.
    :param expires_delta: Время жизни токена в минутах (по умолчанию из настроек).
    :return: Строка JWT access-токена.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=expires_delta or settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    
    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])
    
    to_encode.update({"exp": expire, "token_type": "access"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """
    Создает JWT refresh-токен.

    :param data: Данные, которые будут зашифрованы в токене.
    :return: Строка JWT refresh-токена.
    """
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = data.copy()
    to_encode.update({"exp": expire, "token_type": "refresh"})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

