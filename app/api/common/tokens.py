import secrets
from datetime import datetime, timedelta

from app.core.settings import settings


class TokenService:
    """Сервис для генерации и управления токенами."""

    @staticmethod
    def generate_restoration_token() -> str:
        """Генерирует криптографически безопасный токен восстановления."""
        return secrets.token_urlsafe(32)

    @staticmethod
    def get_restoration_token_expiration() -> datetime:
        """Возвращает время истечения срока действия токена восстановления."""
        return datetime.now() + timedelta(days=settings.RESTORATION_TOKEN_EXPIRE_DAYS)