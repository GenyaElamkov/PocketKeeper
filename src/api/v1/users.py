from fastapi import APIRouter, Depends, status

from src.core.dependencies import (get_current_admin, get_current_user,
                                   get_user_service)
from src.schemas.users import User, UserList, UserRequest, UserUpdate
from src.services.users import UserService

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@router.get("/", name="Список пользователей",
            response_model=UserList)
async def get_all_users(
    request: UserRequest = Depends(),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_admin),
) -> UserList:
    """Получение списка пользователей, может только 'user' с ролью 'admin'."""
    return await user_service.get_all_users(request)


@router.get("/me",
            name="Текущий пользователь",
            response_model=User)
async def get_current_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Получение текущего пользователя."""
    return current_user


@router.get("/{user_id}",
            name="Пользователь",
            response_model=User,
            deprecated=True)
async def get_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> User:
    """Получение пользователя по ID."""
    return await user_service.get_user_by_id(current_user_id=current_user.id, user_id=user_id)


@router.put("/{user_id}",
            name="Обновить пользователя",
            response_model=User)
async def update_user(
    user_id: int,
    user: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> User:
    """Обновление пользователя."""
    return await user_service.update_user(
        user_id=user_id,
        current_user_id=current_user.id,
        user=user)


@router.delete("/{user_id}",
               name="Удалить пользователя",
               response_model=User,
               status_code=status.HTTP_200_OK)
async def delete_user(
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> User:
    """Удаление пользователя. Удалить пользователя может 'admin' или сам пользователь."""
    return await user_service.delete_user(user_id, current_user.id, current_user.role)
