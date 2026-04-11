import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db_depends import get_async_db
from src.auth import (create_access_token, create_refresh_token, hash_pasword,
                      verify_password)
from src.config import ALGORITHM, SECRET_KEY
from src.models.users import User as UserModel
from src.schemas.users import RefreshTokenRequest as RefreshTokenRequestSchema
from src.schemas.users import User as UserSchema
from src.schemas.users import UserCreate as UserCreateSchema
from src.schemas.users import UserUpdate as UserUpdateSchema

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@router.post("/", name="Создать пользователя",
             response_model=UserSchema,
             status_code=status.HTTP_201_CREATED)
async def create_user(user: UserCreateSchema,
                      db: AsyncSession = Depends(get_async_db)) -> UserSchema:
    """Создание пользователя."""
    user_result = await db.scalars(
        select(UserModel).where(
            UserModel.email == user.email,
        ),
    )
    if user_result.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Пользователь с таким email уже существует",
        )

    db_user = UserModel(
        email=user.email,
        hashed_password=hash_pasword(user.password.get_secret_value()),
        full_name=user.full_name,
        role=user.role,
    )
    db.add(db_user)
    await db.commit()
    return db_user


@router.get("/", name="Список пользователей",
            response_model=list[UserSchema])
async def get_all_users(db: AsyncSession = Depends(get_async_db)) -> list[UserSchema]:
    """Получение списка пользователей."""
    result = await db.scalars(select(UserModel))
    users = result.all()
    if users is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователи не найдены",
        )
    return users


@router.put("/{user_id}",
            name="Обновить пользователя",
            response_model=UserSchema)
async def update_user(user_id: int, user: UserUpdateSchema,
                      db: AsyncSession = Depends(get_async_db)) -> UserSchema:
    """Обновление пользователя."""
    user_result = await db.scalars(
        select(UserModel).where(UserModel.id == user_id),
    )
    db_user = user_result.first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    await db.execute(
        update(UserModel)
        .where(UserModel.id == user_id)
        .values(
            email=user.email,
            hashed_password=hash_pasword(str(user.password)),
            full_name=user.full_name,
            is_active=user.is_active,
        ),
    )
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.delete("/{user_id}", name="Удалить пользователя",
               response_model=UserSchema)
async def delete_user(user_id: int,
                      db: AsyncSession = Depends(get_async_db)) -> UserSchema:
    """Удаление пользователя."""
    user = await db.scalars(
        select(UserModel).where(UserModel.id == user_id, UserModel.is_active.is_(True)),
    )
    db_user = user.first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    db_user.is_active = False
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.post("/token",
             name="Аутентифицирует пользователя")
async def login(
    form_date: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_async_db),
) -> dict:
    """Аутентификация пользователя."""
    result = await db.scalars(
        select(UserModel).where(UserModel.email == form_date.username, UserModel.is_active.is_(True)),
    )
    user = result.first()
    if not user or not verify_password(form_date.password, user.hashed_password):
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


async def get_current_user_from_refresh_token(
        token: str,
        db: AsyncSession,
) -> UserModel:
    """Проверка токена и возврат пользователя."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Неверный токен",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str | None = payload.get("sub")
        token_type: str | None = payload.get("token_type")
        if email is None or token_type != "refresh":
            raise credentials_exception

    except jwt.ExpiredSignatureError:
        raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception

    result = await db.scalars(
        select(UserModel).where(UserModel.email == email,
                                UserModel.is_active.is_(True)),
    )
    user = result.first()
    if user is None:
        raise credentials_exception
    return user


@router.post("/refresh-token",
             name="Обновление токена")
async def refresh_token(body: RefreshTokenRequestSchema,
                        db: AsyncSession = Depends(get_async_db)) -> dict:
    """Обновляет refresh-токен, принимая старый refresh-токен в теле запроса."""
    old_refresh_token = body.refresh_token
    user = get_current_user_from_refresh_token(old_refresh_token, db)
    new_refresh_token = create_refresh_token(
        data={"sub": user.email, "role": user.role, "id": user.id},
    )
    return {
        "refresh_token": new_refresh_token,
        "token_type": "bearer",
    }


@router.post("/refresh-access-token", name="Обновление access токена")
async def refresh_access_token(body: RefreshTokenRequestSchema,
                               db: AsyncSession = Depends(get_async_db)) -> dict:
    """Обновляет access-токен, принимая старый refresh-токен в теле запроса."""
    old_refresh_token = body.refresh_token
    user = get_current_user_from_refresh_token(old_refresh_token, db)
    new_access_token = create_access_token(
        data={"sub": user.email, "role": user.role, "id": user.id},
    )
    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }
