from collections.abc import Sequence

from fastapi import HTTPException, status

from src.models.categories import Category
from src.repositories.categories import CategoryRepository
from src.schemas.categories import CategoryCreate


class CategoryService:
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    async def get_categories_by_user(self, user_id: int) -> Sequence[Category]:
        """Получить все категории конкретного пользователя."""
        db_categories = await self.category_repo.get_all_by_user_id(user_id)
        return db_categories

    async def create_category(self, category: CategoryCreate, user_id: int) -> Category | None:
        """Создать категорию."""
        # Проверяем, что родительская категория принадлежит пользователю
        # и существует
        if category.parent_id is not None:
            parent_category = await self.category_repo.get_parent_category(category.parent_id)
            if not parent_category:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent category with id {category.parent_id} not found",
                )
            if parent_category.user_id != user_id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can't create a category for another user",
                )
        return await self.category_repo.create(**category.model_dump(), user_id=user_id)
