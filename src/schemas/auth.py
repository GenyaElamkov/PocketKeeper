from pydantic import BaseModel, Field


class RefreshTokenRequest(BaseModel):
    """Модель для обновления токена"""
    refresh_token: str = Field(..., description="Токен обновления")
