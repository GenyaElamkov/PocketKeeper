from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.api.v1.db_depends import get_async_db
from backend.src.auth import (create_access_token, create_refresh_token,
                              get_current_user_by_refresh_token,
                              verify_password)
from backend.src.models.users import User as UserModel

router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация"],
)


@router.post("/token", name="Аутентифицирует пользователя")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db),
) -> dict:
    """Аутентификация пользователя."""
    result = await db.scalars(
        select(UserModel).where(UserModel.email == form_data.username, UserModel.is_active.is_(True)),
    )
    user = result.first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный логин или пароль",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
    refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role, "id": user.id})
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh-token", name="Обновление токена")
async def refresh_token(
    user: UserModel = Depends(get_current_user_by_refresh_token),
) -> dict:
    """Обновляет refresh-токен, принимая старый refresh-токен в теле запроса."""
    new_refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.role, "id": user.id},
    )
    return {
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh-access-token", name="Обновление access токена")
async def refresh_access_token(
    user: UserModel = Depends(get_current_user_by_refresh_token),
) -> dict:
    """Обновляет access-токен, принимая старый refresh-токен в теле запроса."""
    new_access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id},
    )
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }
