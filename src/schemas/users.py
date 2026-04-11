from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr


class UserRole(str, Enum):
    admin = "admin"
    member = "member"


class UserCreate(BaseModel):
    """Модель для создания пользователя"""
    email: EmailStr = Field(..., description="Email для входа")
    password: SecretStr = Field(..., min_length=8, description="Пароль (минимум 8 символов)")
    full_name: str = Field(..., max_length=254, description="Полное имя пользователя")
    role: UserRole = Field(default=UserRole.member, description="Роль")


class User(BaseModel):
    """Модель для вывода пользователя"""
    id: int = Field(..., description="Уникальный идентификатор пользователя")   # noqa
    email: EmailStr = Field(..., description="Email для входа")
    full_name: str = Field(..., description="Полное имя пользователя")
    is_active: bool = Field(..., description="Активен ли аккаунт")
    role: UserRole = Field(..., description="Роль")
    created_at: datetime = Field(..., description="Дата регистрации")
    updated_at: datetime = Field(..., description="Дата обновления данных")

    model_config = ConfigDict(from_attributes=True)


class UserUpdate(BaseModel):
    """Модель для обновления пользователя"""
    email: EmailStr | None = Field(None, description="Email для входа")
    password: SecretStr | None = Field(None, min_length=8, description="Пароль (минимум 8 символов)")
    full_name: str | None = Field(None, max_length=254, description="Полное имя пользователя")
    is_active: bool | None = Field(None, description="Активен ли аккаунт")
    role: UserRole | None = Field(None, description="Роль")


class RefreshTokenRequest(BaseModel):
    refresh_token: str = Field(..., description="Токен обновления")
