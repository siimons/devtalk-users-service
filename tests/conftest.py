import pytest
import pytest_asyncio
from httpx import AsyncClient

from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.v1.views import router
from app.core.dependencies import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Настройка жизненного цикла приложения для тестов.
    """
    await db.connect()
    yield
    await db.close()


@pytest.fixture
def app() -> FastAPI:
    """
    Создаёт экземпляр приложения FastAPI с подключённым роутером.
    """
    app = FastAPI(lifespan=lifespan)
    app.include_router(router, prefix="/api/v1")
    return app


@pytest_asyncio.fixture
async def client(app: FastAPI):
    """
    Асинхронный клиент для тестирования.
    """
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    """
    Фикстура для подготовки базы данных перед каждым тестом.
    """
    await db.connect()
    async with db.pool.acquire() as connection:
        async with connection.cursor() as cursor:
            await cursor.execute("SET FOREIGN_KEY_CHECKS=0;")
            tables = ["users", "articles", "tags", "article_tags", "comments"]
            for table in tables:
                await cursor.execute(f"TRUNCATE TABLE {table};")
            await cursor.execute("SET FOREIGN_KEY_CHECKS=1;")
    yield
    await db.close()


@pytest_asyncio.fixture
async def create_test_user():
    """
    Фикстура для создания тестового пользователя в базе данных.
    """
    query = """
        INSERT INTO users (username, email, password)
        VALUES (%s, %s, %s)
    """
    args = ("testuser", "test@example.com", "hashedpassword")
    user_id = await db.execute(query, *args)

    query = "SELECT id, username, email FROM users WHERE id = %s"
    user = await db.fetch(query, user_id)
    return user[0]
