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

    async def get_parent_category(self, parent_id: int) -> Category | None:
        """Получить родительскую категорию."""
        return await self.db.scalar(select(Category).where(Category.id == parent_id))

    async def create(self, name: str, icon: str, parent_id: id, user_id: int) -> Category:
        """Создать категорию."""
        db_category = Category(
            name=name,
            icon=icon,
            parent_id=parent_id,
            user_id=user_id,
        )
        self.db.add(db_category)
        await self.db.commit()
        await self.db.refresh(db_category)
        return db_category
