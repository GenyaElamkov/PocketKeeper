from fastapi import HTTPException, status
from loguru import logger

from src.repositories.users import UserRepository
from src.schemas.users import (User, UserCreate, UserList, UserRequest,
                               UserRole, UserUpdate)
from src.services.utils import hash_password


class UserService:
    """Сервис для работы с пользователями."""
    def __init__(self, user_repo: UserRepository):
        self.user_repo = user_repo

    async def get_user_by_id(self, current_user_id: int, user_id: int) -> User:
        """Получить пользователя по ID."""
        if current_user_id != user_id:
            logger.warning(f"You {current_user_id} can't access another user's data")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't access another user's data",
            )
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            logger.warning(f"User with id {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        logger.info(f"User data accessed: {user_id} by {current_user_id}")
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
        user_existed = await self.user_repo.user_exists(user.email)
        if user_existed:
            logger.warning(f"Regiestration failed for {user.email}: email alreade exists")
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )
        hashed_password = hash_password(user.password.get_secret_value())
        new_user = await self.user_repo.create(user.email, hashed_password, user.full_name)
        logger.info(f"User registered: {user.id}")
        return new_user

    async def update_user(self, current_user_id: int, user: UserUpdate) -> User:
        """Обновить пользователя."""
        hashed_password = hash_password(user.password.get_secret_value())
        update_user = await self.user_repo.update(
            user_id=current_user_id,
            email=user.email,
            password=hashed_password,
            full_name=user.full_name,
        )
        logger.info(f"User updated: {current_user_id}")
        return update_user

    async def delete_user(self, user_id: int, current_user_id: int, role: str) -> User:
        """Удалить пользователя."""
        user_to_delete = await self.user_repo.get_active_by_id(user_id)
        if user_to_delete is None:
            logger.warning(f"User with id {user_id} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        if role != UserRole.ADMIN and user_to_delete.id != current_user_id:
            logger.warning(f"You {current_user_id} can't delete another user")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't delete another user",
            )
        user = await self.user_repo.delete(user_to_delete)
        logger.info(f"User deleted: {user_id} role {role}")
        return user
