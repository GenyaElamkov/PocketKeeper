import uuid
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, EmailStr, SecretStr



class UserCreate(BaseModel): 
    """Модель для создания пользователя"""
    email: EmailStr = Field(..., description="Email для входа")
    hashed_password: SecretStr = Field(..., description="Хеш пароля")
    full_name: str = Field(..., description="Полное имя пользователя")
    is_active: bool = Field(default=True, description="Активен ли аккаунт")
    created_at: datetime = Field(..., description="Дата регистрации")


class User(UserCreate):
    """Модель для вывода пользователя"""
    id: uuid.UUID = Field(..., description="Уникальный индефикатор пользователя")
   
    model_config = ConfigDict(from_attributes=True)
