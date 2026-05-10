from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.api.v1.db_depends import get_async_db
from backend.src.config import settings
from backend.src.models.users import User as UserModel
from backend.src.schemas.auth import \
    RefreshTokenRequest as RefreshTokenRequestSchema
from backend.src.schemas.users import User as UserSchema
from backend.src.schemas.users import UserRole

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{settings.api.prefix}/auth/token")


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


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_async_db),
) -> UserSchema:
    """Получение текущего пользователя."""
    creditals_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, settings.auth.secret_key, algorithms=[settings.auth.algorithm])
        email: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")
        if email is None or token_type != "access":
            raise creditals_exception
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.PyJWTError:
        raise creditals_exception

    result = await db.scalars(
            select(UserModel).where(UserModel.email == email, UserModel.is_active.is_(True)),
        )
    user = result.first()
    if user is None:
        raise creditals_exception
    return user


async def get_current_member(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    """Получение текущего пользователя с ролью 'member'."""
    if current_user.role != UserRole.MEMBER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have enough permissions",
        )
    return current_user


async def get_current_admin(current_user: UserModel = Depends(get_current_user)) -> UserModel:
    """Получение текущего пользователя с ролью 'admin'."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have enough permissions",
        )
    return current_user


async def get_current_user_by_refresh_token(
        body: RefreshTokenRequestSchema,
        db: AsyncSession = Depends(get_async_db),
) -> UserModel:
    """Проверка токена и возврат пользователя."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        token = body.refresh_token
        payload = jwt.decode(token, settings.auth.secret_key, algorithms=[settings.auth.algorithm])
        email: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")
        if email is None or token_type != "refresh":
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    result = await db.scalars(
        select(UserModel).where(UserModel.email == email, UserModel.is_active.is_(True)),
    )
    user = result.first()
    if user is None:
        raise credentials_exception
    return user
