from fastapi import APIRouter, HTTPException, status

from app.core.database import Database
from app.api.v1.services import UserService

from app.api.v1.schemas import (
    UserCreate,
    UserLogin,
    UserUpdate,
    UserDelete,
    User
)

router = APIRouter()
db = Database()
user_service = UserService()

@router.post("/users", summary="Создать нового пользователя", response_model=dict)
async def create_user_endpoint(user_data: UserCreate):
    """
    Создание нового пользователя.
    ---
    - **email**: Электронная почта нового пользователя.
    - **username**: Имя пользователя.
    - **password**: Пароль пользователя.
    """
    return await user_service.register_user(user_data)