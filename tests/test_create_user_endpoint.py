import pytest
from httpx import AsyncClient
from fastapi import FastAPI, status

from app.api.v1.views import router
from app.core.database import Database

db = Database()


@pytest.fixture
def app() -> FastAPI:
    """
    Создаёт экземпляр приложения FastAPI с подключённым роутером.
    """
    app = FastAPI()

    @app.on_event("startup")
    async def startup_event():
        await db.connect()

    @app.on_event("shutdown")
    async def shutdown_event():
        await db.close()

    app.include_router(router, prefix="/api/v1")
    return app


@pytest.mark.asyncio
async def test_create_user_success(app: FastAPI):
    """
    Тест успешного создания пользователя.
    """
    async with AsyncClient(app=app, base_url="http://testserver") as client:
        payload = {
            "username": "testuser",
            "email": "testuser@example.com",
            "password": "securepassword123"
        }
        response = await client.post("/api/v1/users", json=payload)
        
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data["username"] == payload["username"]
        assert response_data["email"] == payload["email"]
        assert "id" in response_data
