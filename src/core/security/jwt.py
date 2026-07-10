from datetime import datetime, timedelta, timezone

import jwt

from src.core.config import settings


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
    """Создание refresh-токена с длинным сроком действия token_type='refresh'."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=settings.auth.refresh_token_expire_days)
    to_encode.update({
        "exp": expire,
        "token_type": "refresh",
    })
    return jwt.encode(to_encode, settings.auth.secret_key, algorithm=settings.auth.algorithm)


def create_reset_token(data: dict) -> str:
    """Создание reset-токена с коротким сроком действия token_type='reset'."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.auth.reset_token_expire_minutes)
    to_encode.update({
        "exp": expire,
        "token_type": "reset",
    })
    return jwt.encode(to_encode, settings.auth.secret_key, algorithm=settings.auth.algorithm)
