import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.v1.views import router
from app.core.dependencies import db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Настройка жизненного цикла приложения.
    """
    await db.connect()
    yield
    await db.close()


def create_application() -> FastAPI:
    app = FastAPI(
        title="Dev Talk API - Users",
        description="RESTful API for managing users",
        version="1.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
        lifespan=lifespan,
    )
    app.include_router(router, prefix="/api/v1", tags=["Users"])
    return app


app = create_application()


if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        log_level="info",
        reload=True
    )