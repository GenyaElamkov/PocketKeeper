from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db_depends import get_async_db
from src.auth import get_current_member
from src.models.categories import Category as CategoryModel
from src.models.users import User as UserModel
from src.schemas.categories import Category as CategorySchema
from src.schemas.categories import CategoryCreate as CategoryCreateSchema
from src.schemas.categories import CategoryList as CategoryListSchema
from src.schemas.categories import CategoryRequest as CategoryRequestSchema
from src.schemas.categories import CategoryUpdate as CategoryUpdateSchema

router = APIRouter(
    prefix="/categories",
    tags=["Категории"],
)


@router.post("/", name="Создать новую категорию",
             response_model=CategorySchema,
             status_code=status.HTTP_201_CREATED)
async def create_category(
    category: CategoryCreateSchema,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_member),
) -> CategorySchema:

    if category.parent_id is not None:
        parent = await db.scalars(
            select(CategoryModel).where(CategoryModel.id == category.parent_id),
        )
        if not parent.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Родительская категория не найдена",
            )
    db_category = CategoryModel(**category.model_dump(), user_id=current_user.id)
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


@router.get("/", name="Получить все категории",
            response_model=CategoryListSchema)
async def get_all_categories(
    request: CategoryRequestSchema = Depends(),
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_member),
) -> CategoryListSchema:
    """Получение всех категорий"""
    filters = [CategoryModel.user_id == current_user.id]

    if request.category_id is not None:
        filters.append(CategoryModel.id == request.category_id)

    total_stmt = select(func.count()).select_from(CategoryModel).where(*filters)
    total = await db.scalar(total_stmt) or 0
    categories_stmt = (
        select(CategoryModel)
        .where(*filters)
        .order_by(CategoryModel.name)
        .offset((request.page - 1) * request.page_size)
        .limit(request.page_size)
    )

    items = (await db.scalars(categories_stmt)).all()
    return {
        'items': items,
        'total': total,
        'page': request.page,
        'page_size': request.page_size,
    }


@router.put("/{category_id}", name="Обновить категорию", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category: CategoryUpdateSchema,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_member),
) -> CategorySchema:
    """Обновление категории"""
    result = await db.scalars(
        select(CategoryModel).where(CategoryModel.id == category_id),
    )
    db_category = result.first()
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена",
        )
    if db_category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления категории",
        )
    await db.execute(
        update(CategoryModel)
        .where(CategoryModel.id == category_id)
        .values(**category.model_dump()),
    )
    await db.commit()
    await db.refresh(db_category)
    return db_category


@router.delete("/{category_id}", name="Удалить категорию", response_model=CategorySchema)
async def delete_category(
    category_id: int,
    db: AsyncSession = Depends(get_async_db),
    current_user: UserModel = Depends(get_current_member),
) -> CategorySchema:
    """Удаление категории"""
    category = await db.scalars(
        select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active.is_(True)),
    )
    db_category = category.first()
    if db_category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена",
        )
    if db_category.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления категории",
        )
    db_category.is_active = False
    await db.commit()
    await db.refresh(db_category)
    return db_category
