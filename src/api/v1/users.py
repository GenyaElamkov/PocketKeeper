from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.dependencies import get_async_db
from src.models.users import User as UserModel
from src.schemas.users import User as UserSchema
from src.schemas.users import UserCreate as UserCreateSchema
from src.schemas.users import UserList as UserListSchema
from src.schemas.users import UserRequest as UserRequestSchema
from src.schemas.users import UserRole
from src.schemas.users import UserUpdate as UserUpdateSchema
from src.services.auth import (get_current_admin, get_current_user,
                               hash_password)

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@router.post("/", name="Создать пользователя",
             response_model=UserSchema,
             status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreateSchema,
    db: AsyncSession = Depends(get_async_db),
) -> UserSchema:
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
    )
    db.add(db_user)
    await db.commit()
    return db_user


@router.get("/", name="Список пользователей",
            response_model=UserListSchema)
async def get_all_users(
    request: UserRequestSchema = Depends(),
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_admin),
) -> UserListSchema:
    """Получение списка пользователей, может только 'user' с ролью 'admin'."""
    total_stmt = select(func.count()).select_from(UserModel)
    total = await db.scalar(total_stmt) or 0
    users_stmt = (
        select(UserModel)
        .order_by(
            UserModel.is_active.is_(True).desc(),
            UserModel.email,
        )
        .offset((request.page - 1) * request.page_size)
        .limit(request.page_size)
    )
    items = (await db.scalars(users_stmt)).all()
    return {
        "items": items,
        "total": total,
        'page': request.page,
        'page_size': request.page_size,
    }


@router.get("/{user_id}",
            name="Пользователь",
            response_model=UserSchema)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user),
) -> UserSchema:
    """Получение пользователя по ID."""
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Нет доступа к просмотру этого пользователя",
        )
    stmt = await db.scalars(
        select(UserModel).where(UserModel.id == user_id),
    )
    user = stmt.first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    return user


@router.put("/{user_id}",
            name="Обновить пользователя",
            response_model=UserSchema)
async def update_user(
    user_id: int, user: UserUpdateSchema,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user),
) -> UserSchema:
    """Обновление пользователя."""
    stmt = await db.scalars(
        select(UserModel).where(UserModel.id == user_id),
    )
    db_user = stmt.first()
    if db_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    if db_user.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления пользователя",
        )
    await db.execute(
        update(UserModel)
        .where(UserModel.id == user_id)
        .values(
            email=user.email,
            hashed_password=hash_password(user.password.get_secret_value()),
            full_name=user.full_name,
        ),
    )
    await db.commit()
    await db.refresh(db_user)
    return db_user


@router.delete("/{user_id}", name="Удалить пользователя",
               response_model=UserSchema)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_user),
) -> UserSchema:
    """Удаление пользователя. Удалить пользователя может 'admin' или сам пользователь."""

    user = await db.scalars(
        select(UserModel).where(
            UserModel.id == user_id,
            UserModel.is_active.is_(True)),
    )
    user_to_delete = user.first()
    if user_to_delete is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    if current_user.role != UserRole.ADMIN and user_to_delete.id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления пользователя",
        )
    user_to_delete.is_active = False
    await db.commit()
    await db.refresh(user_to_delete)
    return user_to_delete
