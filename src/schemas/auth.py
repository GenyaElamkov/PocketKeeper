from pydantic import BaseModel, Field, SecretStr


class RefreshTokenRequest(BaseModel):
    """Модель для обновления токена"""
    refresh_token: str = Field(..., description="Токен обновления")


class ResetPasswordRequest(BaseModel):
    """Модель для сброса пароля"""
    token: str = Field(..., description="Токен сброса пароля")
    password: SecretStr = Field(..., min_length=8, description="Новый пароль (минимум 8 символов)")
