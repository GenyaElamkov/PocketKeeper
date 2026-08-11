import jwt
from fastapi import HTTPException, status
from loguru import logger

from src.core.config import settings
from src.core.security.jwt import (create_access_token, create_refresh_token,
                                   create_reset_token)
from src.core.security.password import hash_password, verify_password
from src.infrastructure.infra_email import SMTPEmailService
from src.repositories.users import UserRepository
from src.schemas.users import User, UserRole, UserUpdateRefreshToken


class AuthService:
    """Сервис аутентификации."""
    def __init__(
            self,
            user_repo: UserRepository,
            email_service: SMTPEmailService,
    ) -> None:
        self.user_repo = user_repo
        self.email_service = email_service

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

    async def get_current_user_by_reset_token(self, reset_token: str) -> User:
        """Получение текущего пользователя по reset-токену."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный токен",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(
                reset_token,
                settings.auth.secret_key,
                algorithms=[settings.auth.algorithm],
            )
            email: str | None = payload.get("sub")
            token_type: str | None = payload.get("token_type")
            if email is None or token_type != "reset":
                logger.warning(
                    {"event": "get_current_user_by_reset_token_failed", "reason": "invalid token"},
                )
                raise credentials_exception

        except jwt.ExpiredSignatureError:
            logger.warning(
                {"event": "get_current_user_by_reset_token_failed", "reason": "token has expired"},
            )
            raise credentials_exception
        except jwt.PyJWTError:
            logger.warning(
                {"event": "get_current_user_by_reset_token_failed", "reason": "invalid token"},
            )
            raise credentials_exception

        user = await self.user_repo.get_active_by_email(email)
        if user is None:
            logger.warning(
                {"event": "get_current_user_by_reset_token_failed", "reason": "user not found"},
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
        # id в токене должен быть строкой, чтобы избежать проблем с сериализацией в JSON
        access_token = create_access_token(data={"sub": user.email, "role": user.role, "id": str(user.id)})
        refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role, "id": str(user.id)})
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
        # id в токене должен быть строкой, чтобы избежать проблем с сериализацией в JSON
        new_refresh_token = create_refresh_token(data={"sub": user.email, "role": user.role, "id": str(user.id)})
        logger.info(
            {"event": "update_refresh_token_success", "user_id": user.id},
        )
        return {
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
        }

    async def update_access_token(self, user: UserUpdateRefreshToken) -> dict:
        """Обновление access-токена."""
        # id в токене должен быть строкой, чтобы избежать проблем с сериализацией в JSON
        new_access_token = create_access_token(
            data={
                "sub": user.email,
                "role": user.role,
                "id": str(user.id),
            },
        )
        logger.info(
            {"event": "update_access_token_success", "user_id": user.id},
        )
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
        }

    async def forgot_password(self, email: str) -> dict:
        """Забыли пароль. Отправка письма с инструкциями по сбросу пароля."""
        logger.info(
            {"event": "forgot_password_attempt", "email": email},
        )

        user = await self.user_repo.get_active_by_email(email)
        if not user:
            logger.info(
                {"event": "forgot_password_unknown_email"},
            )
            return {"message": "Инструкции отправлены на почту."}
        # id в токене должен быть строкой, чтобы избежать проблем с сериализацией в JSON
        raw_token = create_reset_token(
            data={
                "sub": user.email,
                "role": user.role,
                "id": str(user.id),
            },
        )
        reset_link = f"{settings.frontend.url}/reset-password?token={raw_token}"

        logger.info(
            {"event": "forgot_password_success", "user_id": user.id},
        )
        # Отправка письма с инструкциями по сбросу пароля
        await self.email_service.send_email(
            to_email=user.email,
            subject="Инструкции по сбросу пароля",
            html=reset_link,
        )
        return {
            "message": "Инструкции отправлены на почту.",
        }

    async def reset_password(self, raw_token: str, new_password: str) -> dict:
        """Сброс пароля."""
        logger.info({"event": "reset_password_attempt"})

        user = await self.get_current_user_by_reset_token(raw_token)
        hashed_password = hash_password(new_password)
        await self.user_repo.update_password(user.id, hashed_password)

        logger.info({"event": "reset_password_success", "user_id": user.id})
        return {"message": "Пароль успешно изменен"}
