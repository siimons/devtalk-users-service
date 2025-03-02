from fastapi import APIRouter, Request, Response, Depends, status

from app.api.v1.services import UserService

from app.core.dependencies import get_user_service
from app.api.security.rate_limiter import get_rate_limiter
from app.api.common.authentication import get_current_user

from app.api.v1.schemas import (
    UserRegister,
    UserLogin,
    UserUpdate,
    UserDelete,
    UserRestore,
    User,
)

router = APIRouter()


@router.post("/auth/register", response_model=dict, status_code=status.HTTP_201_CREATED)
@get_rate_limiter().limit("20/minute")
async def register_user_endpoint(
    request: Request,
    user_data: UserRegister,
    user_service: UserService = Depends(get_user_service),
):
    """Регистрация нового пользователя."""
    return await user_service.register_user(user_data)


@router.post("/auth/login", response_model=dict, status_code=status.HTTP_200_OK)
@get_rate_limiter().limit("30/minute")
async def login_user_endpoint(
    request: Request,
    response: Response,
    user_data: UserLogin,
    user_service: UserService = Depends(get_user_service),
):
    """Аутентификация пользователя и установка JWT-токенов в cookies."""
    tokens = await user_service.login_user(user_data)

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
    """Выход пользователя из системы. Удаляет JWT-токены из cookies."""
    response = Response(status_code=status.HTTP_204_NO_CONTENT)
    
    response.delete_cookie(key="access_token")
    response.delete_cookie(key="refresh_token")

    return response


@router.get("/users/current", response_model=dict, status_code=status.HTTP_200_OK)
@get_rate_limiter().limit("60/minute")
async def get_user_endpoint(
    request: Request,
    user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Получить данные текущего пользователя."""
    return await user_service.get_user(user["id"])


@router.patch("/users/current", response_model=dict, status_code=status.HTTP_200_OK)
@get_rate_limiter().limit("20/minute")
async def update_user_endpoint(
    request: Request,
    response: Response,
    user_update: UserUpdate,
    user: User = Depends(get_current_user),
    user_service: UserService = Depends(get_user_service),
):
    """Обновить данные текущего пользователя."""
    updated_user = await user_service.update_user(user["id"], user_update)

    if user_update.password:
        response.delete_cookie(key="access_token")
        response.delete_cookie(key="refresh_token")

    return updated_user
