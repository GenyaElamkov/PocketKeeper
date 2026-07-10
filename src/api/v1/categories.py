from typing import List

from fastapi import APIRouter, Depends, Request, status

from src.api.v1.docs.categories import (CREATE_CATEGORY_RESPONSES,
                                        DELETE_CATEGORIES_RESPONSES,
                                        READ_CATEGORIES_RESPONSES,
                                        UPDATE_CATEGORIES_RESPONSES)
from src.core.dependencies import get_category_service, get_current_member
from src.infrastructure.infra_rate_limiter import limiter
from src.schemas.categories import Category, CategoryCreate, CategoryUpdate
from src.schemas.users import User
from src.services.categories import CategoryService

router = APIRouter(
    prefix="/categories",
    tags=["Категории"],
)


@router.get(
        "/",
        name="Получить все категории",
        response_model=List[Category],
        summary="Получить список всех категорий текущего пользователя",
        description="Возвращает все активные категории, принадлежащие авторизованному пользователю. "
                "Включает как родительские категории, так и подкатегории.",
        response_description="Список категорий пользователя",
        responses=READ_CATEGORIES_RESPONSES,
)
@limiter.limit("10/minute")
async def read_categories(
    request: Request,
    category_service: CategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_member),
):
    """Получение всех категорий текущего пользователя."""
    return await category_service.get_categories_by_user(current_user.id)


@router.post(
        "/",
        name="Создать новую категорию",
        response_model=Category,
        status_code=status.HTTP_201_CREATED,
        summary="Создать новую категорию",
        description="Создаёт новую категорию (или подкатегорию) для текущего пользователя. "
                "Можно указать `parent_id` для создания подкатегории. "
                "Имя категории должно быть уникальным в пределах пользователя.",
        response_description="Данные созданной категории",
        responses=CREATE_CATEGORY_RESPONSES,
)
@limiter.limit("5/minute")
async def create_category(
    request: Request,
    category: CategoryCreate,
    category_service: CategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_member),
) -> Category:
    """Создание новой категории."""
    return await category_service.create_category(category, current_user.id)


@router.put(
        "/{category_id}",
        name="Обновить категорию",
        response_model=Category,
        summary="Обновить существующую категорию",
        description="Изменяет название и/или эмодзи категории. "
                "Нельзя изменить `parent_id` через этот эндпоинт.",
        response_description="Обновлённые данные категории",
        responses=UPDATE_CATEGORIES_RESPONSES,
)
@limiter.limit("5/minute")
async def update_category(
    request: Request,
    category_id: int,
    category: CategoryUpdate,
    category_service: CategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_member),
) -> Category:
    """Обновление категории"""
    return await category_service.update_category(category_id, category, current_user.id)


@router.delete(
        "/{category_id}",
        name="Удалить категорию",
        response_model=Category,
        summary="Удалить (архивировать) категорию",
        description="Мягкое удаление категории. Категория становится неактивной, "
                "но остаётся в базе для истории транзакций.",
        response_description="Данные удалённой (архивированной) категории",
        responses=DELETE_CATEGORIES_RESPONSES,
)
@limiter.limit("5/minute")
async def delete_category(
    request: Request,
    category_id: int,
    category_service: CategoryService = Depends(get_category_service),
    current_user: User = Depends(get_current_member),
) -> Category:
    """Удаление категории"""
    return await category_service.delete_category(category_id, current_user.id)
