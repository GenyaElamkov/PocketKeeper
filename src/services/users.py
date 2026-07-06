from fastapi import HTTPException, status
from loguru import logger

from src.repositories.users import UserRepository
from src.schemas.users import (User, UserCreate, UserList, UserRequest,
                               UserRole, UserUpdate, UserUpdatePassword)
from src.services.utils import hash_password, verify_password


class UserService:
    """Сервис для работы с пользователями."""
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_by_id(self, current_user_id: int, user_id: int) -> User:
        """Получить пользователя по ID."""
        logger.info({"event": "get_user_by_id_attempt", "user_id": user_id})
        if current_user_id != user_id:
            logger.warning(
                {"event": "get_user_by_id_failed", "user_id": user_id, "reason": "permission denied"})
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't access another user's data",
            )
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            logger.warning(
                {"event": "get_user_by_id_failed", "user_id": user_id, "reason": "user not found"})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        logger.info(
            {"event": "get_user_by_id_success", "user_id": current_user_id})
        return user

    async def get_all_users(self, request: UserRequest) -> UserList:
        """Получить всех пользователей."""
        items, total = await self.user_repo.get_all(
            page=request.page,
            page_size=request.page_size,
        )
        return {
            "items": items,
            "total": total,
            'page': request.page,
            'page_size': request.page_size,
        }

    async def create_user(self, user: UserCreate) -> User:
        """Создать пользователя."""
        logger.info({"event": "user_creation_attempt", "user_id": user.email})

        user_existed = await self.user_repo.user_exists(user.email)
        if user_existed:
            logger.warning(
                {"event": "user_creation_failed", "user_id": user.email, "reason": "already exists"})
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )
        hashed_password = hash_password(user.password.get_secret_value())
        new_user = await self.user_repo.create(user.email, hashed_password, user.full_name)

        logger.info({"event": "user_creation_success", "user_id": new_user.id})
        return new_user

    async def update_user_profile(self, current_user_id: int, user: UserUpdate) -> User:
        """Обновить пользователя."""
        logger.info({"event": "user_updation_attempt", "user_id": current_user_id})

        is_email_taken = await self.user_repo.user_exists(user.email) if user.email else None
        current_user_email = (await self.user_repo.get_by_id(current_user_id)).email

        if is_email_taken and user.email != current_user_email:
            logger.warning(
                {"event": "user_updation_failed", "user_id": current_user_id, "reason": "email already exists"})
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )

        update_user = await self.user_repo.update(
            user_id=current_user_id,
            email=user.email,
            full_name=user.full_name,
        )

        logger.info({"event": "user_updation_success", "user_id": current_user_id})
        return update_user

    async def update_user_password(self, current_user_id: int, user_update_data: UserUpdatePassword) -> User:
        """Обновить пароль пользователя."""
        logger.info({"event": "user_password_updation_attempt", "user_id": current_user_id})

        # Проверяем, что старый пароль совпадает с текущим паролем пользователя
        user = await self.user_repo.get_by_id(current_user_id)
        if not user or not verify_password(user_update_data.old_password.get_secret_value(), user.hashed_password):
            logger.warning(
                {
                    "event": "user_password_updation_failed",
                    "user_id": current_user_id,
                    "reason": "old password is incorrect",
                })
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Old password is incorrect",
            )

        hashed_password = hash_password(user_update_data.password.get_secret_value())
        update_user = await self.user_repo.update_password(
            user_id=current_user_id,
            password=hashed_password,
        )

        logger.info({"event": "user_password_updation_success", "user_id": current_user_id})
        return update_user

    async def delete_user(self, user_id: int, current_user_id: int, role: str) -> User:
        """Удалить пользователя."""
        logger.info({"event": "user_deletion_attempt", "user_id": user_id})
        user_to_delete = await self.user_repo.get_active_by_id(user_id)
        if user_to_delete is None:
            logger.warning(
                {"event": "user_delation_failed", "user_id": user_id, "reason": "user not found"})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        if role != UserRole.ADMIN and user_to_delete.id != current_user_id:
            logger.warning(
                {"event": "user_deletion_failed", "user_id": current_user_id, "reason": "permission denied"})
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't delete another user",
            )
        user = await self.user_repo.delete(user_to_delete)
        logger.info({"event": "user_deletion_success", "user_id": user_id, "reason": role})
        return user
