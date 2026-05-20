from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User


class UserRepository:
    """Репозиторий для работы с пользователями."""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        """Получить пользователя по ID."""
        return await self.db.scalar(
            select(User).filter(User.id == user_id),
        )

    async def get_all(
            self,
            page: int,
            page_size: int,
    ) -> tuple[User, int]:
        """Получить всех пользователей по ID."""
        total_stmt = select(func.count()).select_from(User)
        total = await self.db.scalar(total_stmt) or 0
        users_stmt = (
            select(User)
            .order_by(
                User.is_active.is_(True).desc(),
                User.email,
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = (await self.db.scalars(users_stmt)).all()
        return items, total
