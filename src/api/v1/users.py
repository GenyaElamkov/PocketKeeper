from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.db_depends import get_async_db
from src.auth import hash_password
from src.models.users import User as UserModel
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
        hashed_password=hash_password(user.password.get_secret_value()),
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
            hashed_password=hash_password(str(user.password)),
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
