from fastapi import APIRouter, Depends, Request, status

from src.core.dependencies import (get_current_admin, get_current_user,
                                   get_user_service)
from src.infrastructure.infra_rate_limiter import limiter
from src.schemas.users import (User, UserList, UserRequest, UserUpdate,
                               UserUpdatePassword)
from src.services.users import UserService

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@router.get("/", name="Список пользователей", response_model=UserList)
@limiter.limit("10/minute")
async def get_all_users(
    request: Request,
    user_request: UserRequest = Depends(),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_admin),
) -> UserList:
    """Получение списка пользователей, может только 'user' с ролью 'admin'."""
    return await user_service.get_all_users(user_request)


@router.get("/me", name="Текущий пользователь", response_model=User)
@limiter.limit("10/minute")
async def get_current_user(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> User:
    """Получение текущего пользователя."""
    return current_user


@router.get("/{user_id}", name="Пользователь",
            response_model=User, deprecated=True)
@limiter.limit("10/minute")
async def get_user(
    request: Request,
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> User:
    """Получение пользователя по ID."""
    return await user_service.get_user_by_id(current_user_id=current_user.id, user_id=user_id)


@router.patch("/me", name="Обновить профиль пользователя", response_model=User)
@limiter.limit("5/minute")
async def update_user(
    request: Request,
    user: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> User:
    """Обновление профиля пользователя."""
    return await user_service.update_user(current_user_id=current_user.id, user=user)


@router.patch("/change-password", name="Обновить пароль пользователя", response_model=User)
@limiter.limit("5/minute")
async def update_password_user(
    request: Request,
    user_update_data: UserUpdatePassword,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> User:
    """Обновление пароля пользователя."""
    return await user_service.update_user_password(current_user_id=current_user.id, user_update_data=user_update_data)


@router.delete("/{user_id}", name="Удалить пользователя",
               response_model=User, status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def delete_user(
    request: Request,
    user_id: int,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> User:
    """Удаление пользователя. Удалить пользователя может 'admin' или сам пользователь."""
    return await user_service.delete_user(user_id, current_user.id, current_user.role)
