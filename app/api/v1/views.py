from fastapi import APIRouter, Depends, status

from app.core.database import Database
from app.api.cache.memcached_manager import CacheManager
from app.core.dependencies import get_database, get_cache
from app.api.v1.services import UserService

from app.api.v1.schemas import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserDelete,
    User
)

router = APIRouter()
user_service = UserService()

@router.post("/users", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_user_endpoint(
    user_data: UserCreate,
    db: Database = Depends(get_database)
):
    """
    Создание нового пользователя.
    ---
    - **email**: Электронная почта нового пользователя.
    - **username**: Имя пользователя.
    - **password**: Пароль пользователя.
    """
    return await user_service.register_user(db, user_data)

@router.get("/users/{user_id}", response_model=dict, status_code=status.HTTP_200_OK)
async def get_user_endpoint(
    user_id: int,
    db: Database = Depends(get_database),
    cache: CacheManager = Depends(get_cache)
):
    """
    Получение информации о пользователе по его ID.
    ---
    - **user_id**: Уникальный идентификатор пользователя.
    """
    return await user_service.get_user(db, cache, user_id)