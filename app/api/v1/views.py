from fastapi import APIRouter, Response, Depends, status

from app.core.database import Database
from app.api.cache.memcached_manager import CacheManager

from app.core.dependencies import get_database, get_cache
from app.api.common.auth import get_current_user
from app.api.v1.services import UserService

from app.api.v1.schemas import (
    UserRegister,
    UserLogin,
    UserUpdate,
    UserDelete,
    User
)

router = APIRouter()
user_service = UserService()


@router.post("/auth/register", response_model=dict, status_code=status.HTTP_201_CREATED)
async def register_user_endpoint(
    user_data: UserRegister,
    db: Database = Depends(get_database)
):
    """
    Регистрация нового пользователя.
    """
    return await user_service.register_user(db, user_data)


@router.post("/auth/login", response_model=dict, status_code=status.HTTP_200_OK)
async def login_user_endpoint(
    response: Response,
    user_data: UserLogin,
    db: Database = Depends(get_database)
):
    """
    Аутентификация пользователя и установка JWT-токенов в cookies.
    """
    tokens = await user_service.login_user(db, user_data)

    response.set_cookie(
        key="access_token",
        value=tokens["access_token"],
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=3600,
    )
    response.set_cookie(
        key="refresh_token",
        value=tokens["refresh_token"],
        httponly=True,
        secure=True,
        samesite="Lax",
        max_age=86400,
    )

    return {
        "access_token": tokens["access_token"],
        "token_type": "bearer",
    }


@router.post("/auth/logout", status_code=status.HTTP_204_NO_CONTENT)
async def logout_user_endpoint():
    """
    Выход пользователя из системы. Удаляет JWT-токены из cookies.
    """
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return response


@router.get("/users/current", response_model=dict, status_code=status.HTTP_200_OK)
async def get_user_endpoint(
    user: User = Depends(get_current_user),
    db: Database = Depends(get_database),
    cache: CacheManager = Depends(get_cache)
):
    """
    Получить данные текущего пользователя.
    """
    return await user_service.get_user(db, cache, user)


@router.patch("/users/current", response_model=dict, status_code=status.HTTP_200_OK)
async def update_user_endpoint(
    response: Response,
    user_update: UserUpdate,
    user: User = Depends(get_current_user),
    db: Database = Depends(get_database),
    cache: CacheManager = Depends(get_cache)
):
    """
    Обновить данные текущего пользователя.
    """
    updated_user = await user_service.update_user(db, cache, user, user_update)

    if user_update.password:
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")

    return updated_user
