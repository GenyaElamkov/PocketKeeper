from fastapi import APIRouter, Depends, Request, status
from fastapi.security import OAuth2PasswordRequestForm

from src.api.v1.docs.auth import (CREATE_USER_RESPONSES,
                                  FORGOT_PASSWORD_RESPONSES, LOGIN_RESPONSES,
                                  REFRESH_ACCESS_TOKEN_RESPONSES,
                                  REFRESH_TOKEN_RESPONSES,
                                  RESET_PASSWORD_RESPONSES)
from src.core.dependencies import get_auth_service, get_user_service
from src.infrastructure.infra_rate_limiter import limiter
from src.schemas.auth import RefreshTokenRequest, ResetPasswordRequest
from src.schemas.users import User, UserCreate, UserEmail
from src.services.auth import AuthService
from src.services.users import UserService

router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация"],
)


@router.post(
        "/register",
        name="Создать пользователя",
        response_model=User,
        status_code=status.HTTP_201_CREATED,
        summary='Регистрация нового аккаунта',
        description="Создаёт нового пользователя с указанными email, паролем и именем.",
        response_description="Данные созданного пользователя",
        responses=CREATE_USER_RESPONSES,
)
@limiter.limit("5/minute")
async def create_user(
    request: Request,
    user: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> User:
    """Создание пользователя."""
    return await user_service.create_user(user)


@router.post(
        "/token",
        name="Аутентифицирует пользователя",
        summary="Вход в систему",
        description="Аутентификация по email и паролю. Возвращает access и refresh токены.",
        response_description="Токены доступа и обновления",
        responses=LOGIN_RESPONSES,
)
@limiter.limit("5/minute")
async def login(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """Аутентификация пользователя."""
    return await auth_service.create_login_token(
        email=form_data.username,
        password=form_data.password,
    )


@router.post(
        "/refresh-token",
        name="Обновление токена",
        summary="Обновление refresh-токена",
        description="Принимает действующий refresh-токен и возвращает новый refresh-токен.",
        response_description="Новый refresh-токен",
        responses=REFRESH_TOKEN_RESPONSES,
)
@limiter.limit("5/minute")
async def refresh_token(
    request: Request,
    refresh_request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """Обновляет refresh-токен, принимая старый refresh-токен в теле запроса."""
    user = await auth_service.get_current_user_by_refresh_token(refresh_request.refresh_token)
    return await auth_service.update_refresh_token(user)


@router.post(
        "/refresh-access-token",
        name="Обновление access токена",
        summary="Обновление access-токена",
        description="Принимает действующий refresh-токен и возвращает новый access-токен.",
        response_description="Новый access-токен",
        responses=REFRESH_ACCESS_TOKEN_RESPONSES,
)
@limiter.limit("5/minute")
async def refresh_access_token(
    request: Request,
    refresh_request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """Обновляет access-токен, принимая старый refresh-токен в теле запроса."""
    user = await auth_service.get_current_user_by_refresh_token(refresh_request.refresh_token)
    return await auth_service.update_access_token(user)


@router.post(
        "/forgot-password",
        name="Забыли пароль",
        summary="Запрос на сброс пароля",
        description="Отправляет на указанный email ссылку для сброса пароля с токеном.",
        response_description="Сообщение об успешной отправке",
        responses=FORGOT_PASSWORD_RESPONSES,
)
@limiter.limit("5/minute")
async def forgot_password(
    request: Request,
    email_data: UserEmail,
    auth_service: AuthService = Depends(get_auth_service),
):
    """Забыли пароль."""
    return await auth_service.forgot_password(email_data.email)


@router.post(
        "/reset-password",
        name="Сброс пароля",
        summary="Сброс пароля по токену",
        description="Устанавливает новый пароль, используя токен из письма сброса.",
        response_description="Сообщение об успешном сбросе",
        responses=RESET_PASSWORD_RESPONSES,
)
@limiter.limit("5/minute")
async def reset_password(
    request: Request,
    data: ResetPasswordRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """Сброс пароля."""
    return await auth_service.reset_password(
        raw_token=data.token,
        new_password=data.password.get_secret_value(),
    )
