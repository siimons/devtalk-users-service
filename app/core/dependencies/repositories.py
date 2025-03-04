from fastapi import Depends

from app.api.storage.database import Database
from app.api.v1.repositories import UserRepository

from app.core.dependencies.common import get_database


async def get_user_repository(
    db: Database = Depends(get_database),
) -> UserRepository:
    """
    Dependency для получения репозитория пользователей.

    Args:
        db (Database): Объект базы данных.

    Returns:
        UserRepository: Репозиторий пользователей.
    """
    return UserRepository(db)