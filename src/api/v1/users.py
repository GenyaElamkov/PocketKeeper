from fastapi import APIRouter, Depends, Request, status

from src.core.dependencies import (get_current_admin, get_current_user,
                                   get_user_service)
from src.infrastructure.infra_rate_limiter import limiter
from src.schemas.error import ErrorResponse
from src.schemas.users import (User, UserList, UserRequest, UserUpdate,
                               UserUpdatePassword)
from src.services.users import UserService

router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@router.get(
        "/",
        name="Список пользователей",
        response_model=UserList,
        summary="Получить список всех пользователей (только админ)",
        description="Возвращает список пользователей с пагинацией. Доступно только для пользователей с ролью `admin`.",
        response_description="Список пользователей и общее количество",
        responses={
            403: {
                "description": "Недостаточно прав (требуется роль admin)",
                "model": ErrorResponse,
                "content": {
                    "application/json": {
                        "example": {"detail": "You don't have enough permissions"},
                    },
                },
            },
            429: {
                "description": "Слишком много запросов (ограничение 10 в минуту)",
                "model": ErrorResponse,
            },
        },
)
@limiter.limit("10/minute")
async def get_all_users(
    request: Request,
    user_request: UserRequest = Depends(),
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_admin),
) -> UserList:
    """Получение списка пользователей, может только 'user' с ролью 'admin'."""
    return await user_service.get_all_users(user_request)


@router.get(
        "/me",
        name="Текущий пользователь",
        response_model=User,
        summary="Получить профиль текущего пользователя",
        description="Возвращает данные авторизованного пользователя.",
        response_description="Данные пользователя",
        responses={
            401: {
                "description": "Не авторизован (отсутствует или невалидный токен)",
                "model": ErrorResponse,
                "content": {
                    "application/json": {
                        "example": {"detail": "Could not validate credentials"},
                    },
                },
            },
            429: {
                "description": "Слишком много запросов (ограничение 10 в минуту)",
                "model": ErrorResponse,
            },
        },
)
@limiter.limit("10/minute")
async def get_current_user(
    request: Request,
    current_user: User = Depends(get_current_user),
) -> User:
    """Получение текущего пользователя."""
    return current_user


@router.patch(
        "/me",
        name="Обновить профиль пользователя",
        response_model=User,
        summary="Обновить профиль текущего пользователя",
        description="Позволяет изменить email и/или имя пользователя.",
        response_description="Обновлённые данные пользователя",
        responses={
            401: {
                "description": "Не авторизован",
                "model": ErrorResponse,
            },
            409: {
                "description": "Новый email уже занят другим пользователем",
                "model": ErrorResponse,
                "content": {
                    "application/json": {
                        "example": {"detail": "User with this email already exists"},
                    },
                },
            },
            422: {
                "description": "Ошибка валидации данных",
                "model": ErrorResponse,
            },
            429: {
                "description": "Слишком много запросов (ограничение 5 в минуту)",
                "model": ErrorResponse,
            },
        },
)
@limiter.limit("5/minute")
async def update_profile_user(
    request: Request,
    user: UserUpdate,
    user_service: UserService = Depends(get_user_service),
    current_user: User = Depends(get_current_user),
) -> User:
    """Обновление профиля пользователя."""
    return await user_service.update_user_profile(current_user_id=current_user.id, user=user)


@router.patch(
        "/change-password",
        name="Обновить пароль пользователя",
        response_model=User,
        summary="Сменить пароль",
        description="Изменяет пароль текущего пользователя. Требуется указать старый пароль.",
        response_description="Данные пользователя после смены пароля",
        responses={
            401: {
                "description": "Не авторизован",
                "model": ErrorResponse,
            },
            400: {
                "description": "Старый пароль указан неверно",
                "model": ErrorResponse,
                "content": {
                    "application/json": {
                        "example": {"detail": "Old password is incorrect"},
                    },
                },
            },
            422: {
                "description": "Ошибка валидации (например, новый пароль слишком короткий)",
                "model": ErrorResponse,
            },
            429: {
                "description": "Слишком много запросов (ограничение 5 в минуту)",
                "model": ErrorResponse,
            },
        },
)
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
