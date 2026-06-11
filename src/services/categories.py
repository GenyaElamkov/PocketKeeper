from collections.abc import Sequence

from fastapi import HTTPException, status

from src.repositories.categories import CategoryRepository
from src.schemas.categories import Category, CategoryCreate, CategoryUpdate


class CategoryService:
    """Сервис для работы с категориями."""
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    async def get_categories_by_user(self, user_id: int) -> Sequence[Category]:
        """Получить все категории конкретного пользователя."""
        db_categories = await self.category_repo.get_all_active_by_user_id(user_id)
        if not db_categories:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categories not found",
            )
        return db_categories

    async def create_category(self, category: CategoryCreate, user_id: int) -> Category:
        """Создать категорию."""
        # Проверяем, что родительская категория принадлежит пользователю
        # и существует
        if category.parent_id is not None:
            parent_category = await self.category_repo.get_by_id(category.parent_id)
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
        name_category = await self.category_repo.name_exists(
            name=category.name,
            user_id=user_id,
        )
        if name_category:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category with this name already exists",
            )
        return await self.category_repo.create(category.model_dump(exclude_unset=True), user_id=user_id)

    async def update_category(self, category_id: int, category: CategoryUpdate, user_id: int) -> Category:
        """Обновить категорию."""
        db_category = await self.category_repo.get_by_id(category_id)
        if db_category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        if db_category.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't update a category for another user",
            )
        return await self.category_repo.update(category_id, category.model_dump(exclude_unset=True))

    async def delete_category(self, category_id: int, user_id: int) -> Category:
        """Мягко удалить активную категорию."""
        db_category = await self.category_repo.get_by_id(category_id)
        if db_category is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        if db_category.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't delete a category for another user",
            )
        return await self.category_repo.delete(db_category)
