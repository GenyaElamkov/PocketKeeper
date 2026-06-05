from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from src.core.dependencies import get_auth_service, get_user_service
from src.schemas.auth import RefreshTokenRequest
from src.schemas.users import User, UserCreate
from src.services.auth import AuthService
from src.services.users import UserService

router = APIRouter(
    prefix="/auth",
    tags=["Аутентификация"],
)


@router.post("/register", name="Создать пользователя",
             response_model=User,
             status_code=status.HTTP_201_CREATED)
async def create_user(
    user: UserCreate,
    user_service: UserService = Depends(get_user_service),
) -> User:
    """Создание пользователя."""
    return await user_service.create_user(user)


@router.post("/token", name="Аутентифицирует пользователя")
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """Аутентификация пользователя."""
    return await auth_service.create_login_token(
        email=form_data.username,
        password=form_data.password,
    )


@router.post("/refresh-token", name="Обновление токена")
async def refresh_token(
    refresh_request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """Обновляет refresh-токен, принимая старый refresh-токен в теле запроса."""
    user = await auth_service.get_current_user_by_refresh_token(refresh_request.refresh_token)
    return await auth_service.update_refresh_token(user)


@router.post("/refresh-access-token", name="Обновление access токена")
async def refresh_access_token(
    refresh_request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """Обновляет access-токен, принимая старый refresh-токен в теле запроса."""
    user = await auth_service.get_current_user_by_refresh_token(refresh_request.refresh_token)
    return await auth_service.update_access_token(user)


@router.post("/reset-password", name="Сброс пароля")
async def reset_password(
    reset_request: RefreshTokenRequest,
    auth_service: AuthService = Depends(get_auth_service),
) -> dict:
    """Сброс пароля. (Заглушка)"""
