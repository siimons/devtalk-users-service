from pydantic import BaseModel, ConfigDict, Field, EmailStr
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """
    Базовая схема для пользователя.
    """
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email пользователя")

    model_config = ConfigDict(str_strip_whitespace=True)


class UserRegister(UserBase):
    """
    Схема для регистрации нового пользователя.
    """
    password: str = Field(..., min_length=8, description="Пароль пользователя для регистрации")


class UserLogin(BaseModel):
    """
    Схема для аутентификации пользователя.
    """
    email: EmailStr = Field(..., description="Email пользователя для входа")
    password: str = Field(..., min_length=8, description="Пароль пользователя для входа")


class UserUpdate(BaseModel):
    """
    Схема для обновления данных пользователя.
    """
    current_password: Optional[str] = Field(None, min_length=8, description="Текущий пароль для подтверждения изменений")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Новое имя пользователя")
    email: Optional[EmailStr] = Field(None, description="Новый email пользователя")
    password: Optional[str] = Field(None, min_length=8, description="Новый пароль пользователя")

    model_config = ConfigDict(str_strip_whitespace=True)


class UserDelete(BaseModel):
    """
    Схема для удаления аккаунта пользователя.
    """
    current_password: str = Field(..., min_length=8, description="Текущий пароль для подтверждения удаления")

    model_config = ConfigDict(str_strip_whitespace=True)


class User(BaseModel):
    """
    Схема для получения информации о пользователе.
    """
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    email: EmailStr = Field(..., description="Email пользователя")
    created_at: datetime = Field(..., description="Дата и время создания аккаунта")
    updated_at: Optional[datetime] = Field(None, description="Дата и время последнего обновления данных пользователя")
