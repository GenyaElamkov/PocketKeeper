from collections.abc import Sequence

from src.models.categories import Category
from src.repositories.categories import CategoryRepository


class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    async def get_categories_by_user(self, user_id: int) -> Sequence[Category]:
        """Получить все категории конкретного пользователя."""
        db_categories = await self.category_repo.get_all_by_user_id(user_id)
        return db_categories
