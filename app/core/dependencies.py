from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import Depends

from app.api.storage.database import Database
from app.api.storage.redis import RedisManager
from app.api.v1.repositories import UserRepository
from app.api.v1.services import UserService

db = Database()
cache = RedisManager()


async def get_database() -> Database:
    """
    Dependency для получения объекта базы данных.

    Returns:
        Database: Объект базы данных.
    """
    if not db.pool:
        await db.connect()
    return db


async def get_cache() -> RedisManager:
    """
    Dependency для получения объекта кэша.

    Returns:
        RedisManager: Объект кэша.
    """
    if not cache.client:
        await cache.connect()
    return cache


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


@asynccontextmanager
async def lifespan(app) -> AsyncGenerator[None, None]:
    """
    Настройка жизненного цикла приложения.

    Args:
        app (FastAPI): FastAPI-приложение.

    Yields:
        None: Управление жизненным циклом.
    """
    await db.connect()
    await cache.connect()

    yield

    await db.close()
    await cache.close()
