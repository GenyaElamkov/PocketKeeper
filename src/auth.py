from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db_depends import get_async_db
from src.config import (ACCESS_TOKEN_EXPIRE_MINUTES, ALGORITHM,
                        REFRESH_TOKEN_EXPIRE_DAYS, SECRET_KEY)
from src.models.users import User as UserModel
from src.schemas.users import User as UserSchema

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="users/token")


def hash_pasword(password: str) -> str:
    """Хеширование пароля."""
    return pwd_context.hash(password)


def verify_password(plane_password: str, hashed_password: str) -> bool:
    """Проверка пароля."""
    return pwd_context.verify(plane_password, hashed_password)


def create_access_token(data: dict) -> str:
    """Создание токена."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


def create_refresh_token(data: dict) -> str:
    """Создание regresh-токена с длинным сроком действия token_type='refresh'."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({
        "exp": expire,
        "token_type": "refresh",
    })
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


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
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
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


async def get_current_member(current_user: UserModel = Depends(get_current_user)):
    """Получение текущего пользователя  с ролью 'meber'."""
    if current_user.role != "member":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have enough permissions",
        )
    return current_user
