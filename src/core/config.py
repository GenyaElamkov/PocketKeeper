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
    reset_token_expire_minutes: int = int(os.getenv("RESET_TOKEN_EXPIRE_MINUTES"))


class ApiPrefix(BaseModel):
    """Конфигурация префиксов."""
    prefix: str = "/api/v1"


class LogConfig(BaseModel):
    """Конфигурация логирования."""
    path: str = os.getenv("LOG_PATH", "logs")
    name: str = os.getenv("LOG_NAME", "app_{time:YYYY-MM-DD}.log")
    retention: str = os.getenv("LOG_RETENTION", "10 days")
    rotation: str = os.getenv("LOG_ROTATION", "1 day")
    level: str = os.getenv("LOG_LEVEL", "INFO")
    compression: str = os.getenv("LOG_COMPRESSION", "zip")
    log_format: str = os.getenv("MESSAGE_FORMAT", "{message}")
    serialization: str = os.getenv("LOG_SERIALIZATION", True)


class DatabaseConfig(BaseModel):
    """Конфигурация базы данных."""
    host: str = os.getenv("DB_HOST", "localhost")
    port: str = os.getenv("DB_PORT", "5432")
    user: str = os.getenv("DB_USER", "pocketkeeper_user")
    password: str = os.getenv("DB_PASSWORD")
    database: str = os.getenv("POSTGRES_DB", "pocketkeeper_db")

    @property
    def url(self) -> str:
        """Возвращает URL для подключения к базе данных."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class CorsConfig(BaseModel):
    """Конфигурация CORS."""
    allow_origins: list[str] = ["http://localhost:5173"]
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]
    allow_credentials: bool = True


class FrontendConfig(BaseModel):
    """Конфигурация фронтенда."""
    url: str = os.getenv("FRONTEND_URL", "http://localhost:5173")


class Settings(BaseSettings):
    """Настройки приложения."""
    database: DatabaseConfig = DatabaseConfig()
    cors: CorsConfig = CorsConfig()
    auth: AuthConfig = AuthConfig()
    api: ApiPrefix = ApiPrefix()
    frontend: FrontendConfig = FrontendConfig()
    log: LogConfig = LogConfig()


settings = Settings()
