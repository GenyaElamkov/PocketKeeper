import jwt
from fastapi import HTTPException, status
from loguru import logger

from src.core.config import settings
from src.repositories.users import UserRepository
from src.schemas.users import User, UserRole, UserUpdateRefreshToken
from src.services.utils import (create_access_token, create_refresh_token,
                                verify_password)


class AuthService:
    """Сервис аутентификации."""
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_current_user(self, token: str) -> User:
        """Получение текущего пользователя."""
        creditals_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, settings.auth.secret_key, algorithms=[settings.auth.algorithm])
            email: str | None = payload.get("sub")
            token_type: str | None = payload.get("token_type")
            if email is None or token_type != "access":
                logger.warning(
                    {"event": "get_current_user_failed", "reason": "could not validate credentials"})
                raise creditals_exception
        except jwt.ExpiredSignatureError:
            logger.warning(
                    {"event": "get_current_user_failed", "reason": "token has expired"})
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired",
                headers={"WWW-Authenticate": "Bearer"},
            )
        except jwt.PyJWTError:
            logger.warning(
                {"event": "get_current_user_failed", "reason": "could not validate credentials"})
            raise creditals_exception
        user = await self.user_repo.get_active_by_email(email)
        if user is None:
            logger.warning(
                {"event": "get_current_user_failed", "reason": "user not found"})
            raise creditals_exception
        return user

    async def get_current_admin(self, token: str) -> User:
        """Получение текущего пользователя с ролью 'admin'."""
        current_user = await self.get_current_user(token)
        if current_user.role != UserRole.ADMIN:
            logger.warning(
                {"event": "get_current_admin_failed", "reason": "user has no admin permissions"})
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have enough permissions",
            )
        return current_user

    async def get_current_member(self, token: str) -> User:
        """Получение текущего пользователя c ролью 'member'."""
        current_user = await self.get_current_user(token)
        if current_user.role != UserRole.MEMBER:
            logger.warning(
                {"event": "get_current_member_failed", "reason": "user has no member permissions"})
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have enough permissions",
            )
        return current_user

    async def get_current_user_by_refresh_token(self, refresh_token: str) -> User:
        """Получение текущего пользователя по refresh-токену."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(refresh_token, settings.auth.secret_key, algorithms=[settings.auth.algorithm])
            email: str | None = payload.get("sub")
            token_type: str | None = payload.get("token_type")
            if email is None or token_type != "refresh":
                logger.warning(
                    {"event": "get_current_user_by_refresh_token_failed", "reason": "invalid token"},
                )
                raise credentials_exception

        except jwt.ExpiredSignatureError:
            logger.warning(
                {"event": "get_current_user_by_refresh_token_failed", "reason": "token has expired"},
            )
            raise credentials_exception
        except jwt.PyJWTError:
            logger.warning(
                {"event": "get_current_user_by_refresh_token_failed", "reason": "invalid token"},
            )
            raise credentials_exception

        user = await self.user_repo.get_active_by_email(email)
        if user is None:
            logger.warning(
                {"event": "get_current_user_by_refresh_token_failed", "reason": "user not found"},
            )
            raise credentials_exception
        return user

    async def create_login_token(self, email: str, password: str) -> dict:
        """Создание токена."""
        user = await self.user_repo.get_active_by_email(email)

        if not user or not verify_password(
            plane_password=password,
            hashed_password=user.hashed_password,
        ):
            logger.warning(
                {"event": "create_login_token_failed", "reason": "invalid credentials"},
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Неверный логин или пароль",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
        refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role, "id": user.id})
        logger.info(
            {"event": "create_login_token_success", "user_id": user.id},
        )
        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def update_refresh_token(self, user: UserUpdateRefreshToken) -> dict:
        """Обновление refresh-токена."""
        new_refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role, "id": user.id})
        logger.info(
            {"event": "update_refresh_token_success", "user_id": user.id},
        )
        return {
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    async def update_access_token(self, user: UserUpdateRefreshToken) -> dict:
        """Обновление access-токена."""
        new_access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": user.id})
        logger.info(
            {"event": "update_access_token_success", "user_id": user.id},
        )
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
        }
