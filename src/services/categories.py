from collections.abc import Sequence
from uuid import UUID

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
            await self._validate_parent(
                parent_id=category.parent_id,
                user_id=user_id,
                event_prefix="category_creation",
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
        if "parent_id" in category.model_fields_set and category.parent_id is not None:
            if category.parent_id == category_id:
                logger.warning(
                    {"event": "category_update_failed", "user_id": user_id, "reason": "parent is self"})
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="A category can't be its own parent",
                )
            if await self.category_repo.has_active_children(category_id):
                logger.warning(
                    {"event": "category_update_failed", "user_id": user_id, "reason": "parent has children"})
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail="This category already has subcategories and can't become a subcategory itself "
                    "(maximum 2 levels of nesting allowed)",
                )

            await self._validate_parent(
                parent_id=category.parent_id,
                user_id=user_id,
                event_prefix="category_update",
            )

        updated_category = await self.category_repo.update(category_id, category.model_dump(exclude_unset=True))

        logger.info({"event": "category_update_success", "user_id": user_id})
        return updated_category

    async def _validate_parent(self, parent_id: int, user_id: UUID, event_prefix: str) -> Category:
        """Валидация родительской категории."""
        """Проверить, что категория с id=parent_id может быть использована как родительская:
        существует, принадлежит пользователю и сама не является подкатегорией
        (в системе допускается не более 2 уровней вложенности: категория -> подкатегория).
        """
        parent_category = await self.category_repo.get_by_id(parent_id)
        if not parent_category:
            logger.warning(
                {"event": f"{event_prefix}_failed", "user_id": user_id, "reason": "parent category not found"})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Parent category with id {parent_id} not found",
            )
        if parent_category.user_id != user_id:
            logger.warning(
                {"event": f"{event_prefix}_failed", "user_id": user_id, "reason": "permission denied"})
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't use a category from another user as a parent",
            )
        if parent_category.parent_id is not None:
            logger.warning(
                {"event": f"{event_prefix}_failed", "user_id": user_id, "reason": "parent is a subcategory"})
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Cannot use a subcategory as a parent category (maximum 2 levels of nesting allowed)",
            )
        return parent_category

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
