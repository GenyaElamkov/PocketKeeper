from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.categories import Category


class CategoryRepository:
    """Репозиторий для работы с категориями."""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, category_id: int) -> Category | None:
        """Получить категорию по ID."""
        result = await self.db.scalar(
            select(Category).filter(Category.id == category_id),
        )
        return result

    async def get_all_active_by_user_id(self, user_id: int) -> Sequence[Category]:
        """Получить все активные категории пользователя."""
        result = await self.db.scalars(
            select(Category).filter(
                Category.user_id == user_id,
                Category.is_active.is_(True),
            ),
        )
        return result.all()

    async def create(self, data: dict, user_id: int) -> Category:
        """Создать категорию."""
        db_category = Category(
            **data,
            user_id=user_id,
        )
        self.db.add(db_category)
        await self.db.commit()
        await self.db.refresh(db_category)
        return db_category

    async def update(self, category_id: int, data: dict) -> Category | None:
        """Обновить категорию."""
        await self.db.execute(
            update(Category)
            .where(Category.id == category_id)
            .values(**data),
        )
        await self.db.commit()
        return await self.get_by_id(category_id)

    async def get_by_id_active(self, category_id: int) -> Category | None:
        """Получить активную категорию по ID."""
        category = await self.db.scalar(
            select(Category).filter(
                Category.id == category_id,
                Category.is_active.is_(True)),
        )
        return category

    async def delete(self, category_id: int) -> Category:
        """Удалить категорию."""
        db_category = await self.get_by_id(category_id)
        db_category.is_active = False
        await self.db.commit()
        await self.db.refresh(db_category)
        return db_category
