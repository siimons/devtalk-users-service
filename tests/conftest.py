import pytest
import pytest_asyncio
from fastapi import FastAPI
from httpx import AsyncClient, ASGITransport

from app.api.v1.views import router
from app.core.dependencies import db, cache, lifespan
from app.api.common.hashing import hash_password


@pytest.fixture
def app() -> FastAPI:
    """
    Создаёт экземпляр FastAPI с подключёнными роутерами.
    """
    app = FastAPI(lifespan=lifespan)
    app.include_router(router, prefix="/api/v1")
    return app


@pytest_asyncio.fixture
async def client(app: FastAPI):
    """
    Создаёт асинхронный HTTP-клиент для тестирования API.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_database():
    """
    Очищает тестовую базу данных перед каждым тестом.
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


@pytest_asyncio.fixture(scope="function", autouse=True)
async def setup_cache():
    """
    Очищает кэш перед каждым тестом.
    """
    await cache.connect()
    await cache.client.flush_all()
    yield
    await cache.close()


@pytest_asyncio.fixture
async def get_test_user_payload():
    """
    Возвращает тестовые данные пользователя.
    """
    return {
        "username": "testuser",
        "email": "test@example.com",
        "password": "securepassword123"
    }


@pytest_asyncio.fixture
async def create_test_user(get_test_user_payload):
    """
    Создаёт тестового пользователя в базе данных и возвращает его.
    """
    query = """
        INSERT INTO users (username, email, password)
        VALUES (%s, %s, %s)
    """
    hashed_password = hash_password(get_test_user_payload["password"])
    args = (
        get_test_user_payload["username"],
        get_test_user_payload["email"],
        hashed_password,
    )
    
    user_id = await db.execute(query, *args)

    query = "SELECT id, username, email FROM users WHERE id = %s"
    user = await db.fetch(query, (user_id,))

    return user[0]


@pytest_asyncio.fixture
async def authenticate_test_user(client: AsyncClient, get_test_user_payload, create_test_user):
    """
    Аутентифицирует тестового пользователя и возвращает JWT-токены в cookies.
    """
    login_payload = {
        "email": get_test_user_payload["email"],
        "password": get_test_user_payload["password"],
    }
    response = await client.post("/api/v1/auth/login", json=login_payload)

    assert response.status_code == 200, f"Ошибка авторизации: {response.text}"

    return response.cookies


@pytest_asyncio.fixture
async def auth_client(client: AsyncClient, authenticate_test_user):
    """
    Возвращает HTTP-клиент с авторизацией через cookies и заголовок Authorization.
    """
    client.cookies.update(authenticate_test_user)
    
    access_token = authenticate_test_user.get("access_token")
    if access_token:
        client.headers.update({"Authorization": f"Bearer {access_token}"})
    
    return client
