from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AuthConfig(BaseSettings):
    """Конфигурация аутентификации."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    algorithm: str = "HS256"
    secret_key: str = Field(validation_alias="SECRET_KEY")
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    reset_token_expire_minutes: int = 15


class ApiPrefix(BaseSettings):
    """Конфигурация префиксов."""
    prefix: str = "/api/v1"


class LogConfig(BaseSettings):
    """Конфигурация логирования."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    path: str = "logs"
    name: str = "app_{time:YYYY-MM-DD}.log"
    retention: str = "30 days"
    rotation: str = "1 day"
    level: str = Field(default="INFO", validation_alias="LOG_LEVEL")
    compression: str = "zip"
    log_format: str = "{message}"
    serialization: bool = True


class DatabaseConfig(BaseSettings):
    """Конфигурация базы данных."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    host: str = Field(default="localhost", validation_alias="DB_HOST")
    port: str = Field(default="5432", validation_alias="DB_PORT")
    user: str = Field(default="pocketkeeper_user", validation_alias="DB_USER")
    password: str = Field(validation_alias="DB_PASSWORD")
    database: str = Field(default="pocketkeeper_db", validation_alias="POSTGRES_DB")
    pool_size: int = 10
    max_overflow: int = 20
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    echo: bool = Field(default=True, validation_alias="DB_ECHO")

    @property
    def url(self) -> str:
        """Возвращает URL для подключения к базе данных."""
        return f"postgresql+asyncpg://{self.user}:{self.password}@{self.host}:{self.port}/{self.database}"


class CorsConfig(BaseSettings):
    """Конфигурация CORS."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    allow_origins: list[str] = Field(default=["http://localhost:5173"], validation_alias="CORS_ALLOW_ORIGINS")
    allow_methods: list[str] = ["*"]
    allow_headers: list[str] = ["*"]
    allow_credentials: bool = True


class FrontendConfig(BaseSettings):
    """Конфигурация фронтенда."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    url: str = "http://localhost:5173"


class EmailConfig(BaseSettings):
    """Конфигурация email."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    host: str = Field(default="smtp.gmail.com", validation_alias="SMTP_HOST")
    port: int = Field(default=587, validation_alias="SMTP_PORT")
    username: str = Field(validation_alias="SMTP_USERNAME")
    password: str = Field(validation_alias="SMTP_PASSWORD")
    sender_email: str = Field(validation_alias="SMTP_FROM_EMAIL")
    sender_name: str = Field(default="Finance API", validation_alias="SMTP_FROM_NAME")
    use_tls: bool = True


class ServerConfig(BaseSettings):
    """Конфигурация сервера."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    host: str = Field(default="0.0.0.0", validation_alias="HOST")
    port: int = Field(default=8000, validation_alias="PORT")


class Settings(BaseSettings):
    """Настройки приложения."""
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    environment: str = Field(default="development", validation_alias="ENVIRONMENT")
    server: ServerConfig = ServerConfig()
    database: DatabaseConfig = DatabaseConfig()
    cors: CorsConfig = CorsConfig()
    auth: AuthConfig = AuthConfig()
    api: ApiPrefix = ApiPrefix()
    frontend: FrontendConfig = FrontendConfig()
    log: LogConfig = LogConfig()
    email: EmailConfig = EmailConfig()

    @property
    def debug(self) -> bool:
        return self.environment != "production"


settings = Settings()
