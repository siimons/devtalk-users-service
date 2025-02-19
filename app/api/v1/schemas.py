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
    password: str = Field(..., min_length=8, description="Пароль пользователя")


class UserLogin(BaseModel):
    """
    Схема для входа пользователя в систему.
    """
    email: EmailStr = Field(..., description="Email пользователя для входа")
    password: str = Field(..., min_length=8, description="Пароль пользователя")


class UserUpdate(BaseModel):
    """
    Схема для обновления информации о пользователе.
    """
    current_password: Optional[str] = Field(None, min_length=8, description="Текущий пароль")
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="Обновлённое имя пользователя")
    email: Optional[EmailStr] = Field(None, description="Обновлённый email пользователя")
    password: Optional[str] = Field(None, min_length=8, description="Обновлённый пароль пользователя")

    model_config = ConfigDict(str_strip_whitespace=True)


class UserDelete(BaseModel):
    """
    Схема для удаления пользователя.
    """
    id: int = Field(..., description="ID пользователя для удаления")


class User(BaseModel):
    """
    Схема для получения информации о пользователе.
    """
    id: int = Field(..., description="Уникальный идентификатор пользователя")
    username: str = Field(..., min_length=3, max_length=50, description="Имя пользователя")
    id: EmailStr = Field(..., description="Email пользователя")
    created_at: datetime = Field(..., description="Дата и время создания пользователя")
    updated_at: Optional[datetime] = Field(None, description="Дата и время последнего обновления пользователя")
