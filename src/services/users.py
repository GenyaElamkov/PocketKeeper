from fastapi import HTTPException, status

from src.repositories.users import UserRepository
from src.schemas.users import User, UserList, UserRequest


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
