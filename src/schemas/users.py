from datetime import datetime
from enum import Enum

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr


class UserRole(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"


class UserCreate(BaseModel):
    """Модель для создания пользователя"""
    email: EmailStr = Field(..., description="Email для входа")
    password: SecretStr = Field(..., min_length=8, description="Пароль (минимум 8 символов)")
    full_name: str = Field(..., max_length=254, description="Полное имя пользователя")


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
    full_name: str | None = Field(None, max_length=254, description="Полное имя пользователя")


class UserUpdatePassword(BaseModel):
    """Обновление пароля пользователем."""
    old_password: SecretStr = Field(..., min_length=8, description="Старый пароль (минимум 8 символов)")
    password: SecretStr = Field(..., min_length=8, description="Пароль (минимум 8 символов)")


class UserList(BaseModel):
    """Модель для списка пользователей"""
    items: list[User] = Field(..., description="Список пользователей")
    total: int = Field(ge=0, description="Общее количество пользователей")
    page: int = Field(ge=1, description="Номер страницы")
    page_size: int = Field(ge=1, description="Количество элементов на странице")


class UserRequest(BaseModel):
    """Модель для фильтрации пользователей"""
    page: int = Field(ge=1, default=1, description="Номер страницы")
    page_size: int = Field(ge=1, le=100, default=20, description="Количество элементов на странице")


class UserUpdateRefreshToken(BaseModel):
    """Модель для обновления токена"""
    id: int = Field(..., description="Уникальный идентификатор пользователя")   # noqa
    email: EmailStr = Field(..., description="Email для входа")
    role: UserRole = Field(..., description="Роль")
