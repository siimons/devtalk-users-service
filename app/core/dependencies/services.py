from fastapi import Depends

from app.api.storage.redis import RedisManager
from app.api.v1.repositories import UserRepository
from app.api.v1.services import UserService

from app.core.dependencies.repositories import get_user_repository
from app.core.dependencies.common import get_cache


async def get_user_service(
    user_repo: UserRepository = Depends(get_user_repository),
    cache: RedisManager = Depends(get_cache),
) -> UserService:
    """
    Dependency для получения сервиса пользователей.

    Args:
        user_repo (UserRepository): Репозиторий пользователей.
        cache (RedisManager): Объект кэша.

    Returns:
        UserService: Сервис пользователей.
    """
    return UserService(user_repo, cache)