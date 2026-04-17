import os

from dotenv import load_dotenv
from pydantic import BaseModel
from pydantic_settings import BaseSettings

load_dotenv()


class AuthConfig(BaseModel):
    algorithm: str = os.getenv("ALGORITHM")
    secret_key: str = os.getenv("SECRET_KEY")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES"))
    refresh_token_expire_days: int = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS"))
    token_url: str = "v1/auth/token"


class Settings(BaseSettings):
    auth: AuthConfig = AuthConfig()


settings = Settings()
