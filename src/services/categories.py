from collections.abc import Sequence

from fastapi import HTTPException, status
from loguru import logger

from src.repositories.categories import CategoryRepository
from src.schemas.categories import Category, CategoryCreate, CategoryUpdate


class CategoryService:
    """Сервис для работы с категориями."""
    def __init__(self, category_repo: CategoryRepository):
        self.category_repo = category_repo

    async def get_categories_by_user(self, user_id: int) -> Sequence[Category]:
        """Получить все категории конкретного пользователя."""
        return await self.category_repo.get_all_active_by_user_id(user_id)

    async def create_category(self, category: CategoryCreate, user_id: int) -> Category:
        """Создать категорию."""
        logger.info({"event": "category_creation_attempt", "user_id": user_id})

        # Проверяем, что родительская категория принадлежит пользователю и существует
        if category.parent_id is not None:
            parent_category = await self.category_repo.get_by_id(category.parent_id)
            if not parent_category:
                logger.warning(
                    {"event": "category_creation_failed", "user_id": user_id, "reason": "parent category not found"})
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Parent category with id {category.parent_id} not found",
                )
            if parent_category.user_id != user_id:
                logger.warning(
                    {"event": "category_creation_failed", "user_id": user_id, "reason": "permission denied"})
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You can't create a category for another user",
                )
        name_category = await self.category_repo.name_exists(
            name=category.name,
            user_id=user_id,
        )
        if name_category:
            logger.warning(
                {"event": "category_creation_failed", "user_id": user_id, "reason": "category already exists"})
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Category with this name already exists",
            )
        new_category = await self.category_repo.create(category.model_dump(exclude_unset=True), user_id=user_id)

        logger.info({"event": "category_creation_success", "user_id": user_id})
        return new_category

    async def update_category(self, category_id: int, category: CategoryUpdate, user_id: int) -> Category:
        """Обновить категорию."""
        logger.info({"event": "category_update_attempt", "user_id": user_id})

        db_category = await self.category_repo.get_by_id(category_id)
        if db_category is None:
            logger.warning(
                    {"event": "category_update_failed", "user_id": user_id, "reason": "category not found"})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        if db_category.user_id != user_id:
            logger.warning(
                    {"event": "category_update_failed", "user_id": user_id, "reason": "permission denied"})
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't update a category for another user",
            )
        updated_category = await self.category_repo.update(category_id, category.model_dump(exclude_unset=True))

        logger.info({"event": "category_update_success", "user_id": user_id})
        return updated_category

    async def delete_category(self, category_id: int, user_id: int) -> Category:
        """Мягко удалить активную категорию."""
        logger.info({"event": "category_deletion_attempt", "user_id": user_id})

        db_category = await self.category_repo.get_by_id(category_id)
        if db_category is None:
            logger.warning(
                    {"event": "category_deletion_failed", "user_id": user_id, "reason": "category not found"})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        if db_category.user_id != user_id:
            logger.warning(
                    {"event": "category_deletion_failed", "user_id": user_id, "reason": "permission denied"})
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't delete a category for another user",
            )
        deleted_category = await self.category_repo.delete(db_category)

        logger.info({"event": "category_deletion_success", "user_id": user_id})
        return deleted_category
