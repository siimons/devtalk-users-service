from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# Схема для создания нового пользователя
class UserCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)

# Схема для отображения информации о пользователе
class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    is_active: bool
    created_at: datetime

# Схема для обновления данных пользователя
class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr]
    password: Optional[str] = Field(None, min_length=6)

class UserLogin(BaseModel):
    email: Optional[EmailStr]
    password: str = Field(..., min_length=6)