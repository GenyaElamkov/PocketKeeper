from typing import List

from fastapi import APIRouter, Depends, status

from src.core.dependencies import get_category_service
from src.models.users import User as UserModel
from src.schemas.categories import Category as CategorySchema
from src.schemas.categories import CategoryCreate as CategoryCreateSchema
from src.schemas.categories import CategoryUpdate as CategoryUpdateSchema
from src.services.categories import CategoryService
from src.services.current import get_current_member

router = APIRouter(
    prefix="/categories",
    tags=["Категории"],
)


@router.get("/", name="Получить все категории", response_model=List[CategorySchema])
async def read_categories(
    category_service: CategoryService = Depends(get_category_service),
    current_user: UserModel = Depends(get_current_member),
):
    """Получение всех категорий текущего пользователя."""
    return await category_service.get_categories_by_user(current_user.id)


@router.post("/", name="Создать новую категорию",
             response_model=CategorySchema,
             status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreateSchema,
    category_service: CategoryService = Depends(get_category_service),
    current_user: UserModel = Depends(get_current_member),
) -> CategorySchema:
    """Создание новой категории."""
    return await category_service.create_category(category, current_user.id)


@router.put("/{category_id}", name="Обновить категорию", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category: CategoryUpdateSchema,
    category_service: CategoryService = Depends(get_category_service),
    current_user: UserModel = Depends(get_current_member),
) -> CategorySchema:
    """Обновление категории"""
    return await category_service.update_category(category_id, category, current_user.id)


@router.delete("/{category_id}", name="Удалить категорию", response_model=CategorySchema)
async def delete_category(
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
    current_user: UserModel = Depends(get_current_member),
) -> CategorySchema:
    """Удаление категории"""
    return await category_service.delete_category(category_id, current_user.id)
