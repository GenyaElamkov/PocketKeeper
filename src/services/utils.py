from datetime import datetime, timedelta, timezone

import jwt
from passlib.context import CryptContext

from src.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеширование пароля."""
    return pwd_context.hash(password)


def verify_password(plane_password: str, hashed_password: str) -> bool:
    """Проверка пароля."""
    return pwd_context.verify(plane_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Создание токена."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.auth.access_token_expire_minutes)
    to_encode.update({
        "exp": expire,
        "token_type": "access",
    })
    return jwt.encode(to_encode, settings.auth.secret_key, algorithm=settings.auth.algorithm)


def create_refresh_token(data: dict) -> str:
    """Создание regresh-токена с длинным сроком действия token_type='refresh'."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.auth.refresh_token_expire_days)
    to_encode.update({
        "exp": expire,
        "token_type": "refresh",
    })
    return jwt.encode(to_encode, settings.auth.secret_key, algorithm=settings.auth.algorithm)
