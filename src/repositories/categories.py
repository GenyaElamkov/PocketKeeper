from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.categories import Category


class CategoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all_by_user_id(self, user_id: int) -> Sequence[Category]:
        """Получить все категории конкретного пользователя."""
        result = await self.db.scalars(
            select(Category).filter(Category.user_id == user_id),
        )
        return result.all()
