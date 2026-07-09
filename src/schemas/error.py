from pydantic import BaseModel, Field


class ErrorResponse(BaseModel):
    """Модель для ошибок"""
    detail: str = Field(..., description="Текст ошибки",
                        example="Пользователь с таким адресом электронной почты уже существует.")
