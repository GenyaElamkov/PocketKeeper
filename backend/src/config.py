import os

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

load_dotenv()


class AuthConfig(BaseModel):
    """Конфигурация аутентификации."""
    algorithm: str = os.getenv("ALGORITHM")
    secret_key: str = os.getenv("SECRET_KEY")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))


class ApiPrefix(BaseModel):
    """Конфигурация префиксов."""
    prefix: str = "/api/v1"


class Settings(BaseSettings):
    """Настройки приложения."""
    auth: AuthConfig = AuthConfig()
    api: ApiPrefix = ApiPrefix()


settings = Settings()
