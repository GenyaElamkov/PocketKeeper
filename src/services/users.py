from fastapi import HTTPException, status

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
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't access another user's data",
            )
        user = await self.user_repo.get_by_id(user_id)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
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
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="User with this email already exists",
            )
        hashed_password = hash_password(user.password.get_secret_value())
        return await self.user_repo.create(user.email, hashed_password, user.full_name)

    async def update_user(self, user_id: int, current_user_id: int, user: UserUpdate) -> User:
        """Обновить пользователя."""
        db_user = await self.user_repo.get_by_id(user_id)
        if db_user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        if db_user.id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't update another user's data",
            )

        hashed_password = hash_password(user.password.get_secret_value())
        return await self.user_repo.update(
            user_id=user_id,
            email=user.email,
            password=hashed_password,
            full_name=user.full_name,
        )

    async def delete_user(self, user_id: int, current_user_id: int, role: str) -> User:
        """Удалить пользователя."""
        user_to_delete = await self.user_repo.get_active_by_id(user_id)
        if user_to_delete is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found",
            )
        if role != UserRole.ADMIN and user_to_delete.id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't delete another user",
            )
        return await self.user_repo.delete(user_to_delete)
