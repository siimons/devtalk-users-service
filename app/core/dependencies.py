from contextlib import asynccontextmanager

from app.core.database import Database
from app.api.cache.memcached_manager import CacheManager

db = Database()
cache = CacheManager()


async def get_database() -> Database:
    """
    Dependency для получения объекта базы данных.
    """
    if not db.pool:
        await db.connect()
    return db


async def get_cache() -> CacheManager:
    """
    Dependency для получения объекта кэша.
    """
    if not cache.client:
        await cache.connect()
    return cache


@asynccontextmanager
async def lifespan(app):
    """
    Настройка жизненного цикла приложения.
    """
    await db.connect()
    await cache.connect()
    yield
    await db.close()
    await cache.close()
