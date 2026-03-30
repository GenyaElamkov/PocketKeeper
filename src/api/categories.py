from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db_depends import get_async_db
from src.models.categories import Category as CategoryModel
from src.models.users import User as UserModel
from src.schemas.categories import Category as CategorySchema
from src.schemas.categories import CategoryCreate as CategoryCreateSchema
from src.schemas.categories import CategoryUpdate as CategoryUpdateSchema

router = APIRouter(
    prefix="/categories",
    tags=["Категории"],
)


@router.post("/", name="Создать новую категорию", response_model=CategorySchema, status_code=status.HTTP_201_CREATED)
async def create_category(category: CategoryCreateSchema, db: AsyncSession = Depends(get_async_db)) -> CategorySchema:
    user = await db.scalars(
        select(UserModel).where(UserModel.id == category.user_id, UserModel.is_active == True), # noqa
    )
    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    if category.parent_id is not None:
        parent = await db.scalars(
            select(CategoryModel).where(CategoryModel.id == category.parent_id),
        )
        if not parent.first():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Родительская категория не найдена",
            )

    result = await db.scalars(
        select(CategoryModel).where(CategoryModel.name == category.name),
    )
    if result.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Категория с таким именем уже существует",
        )
    db_category = CategoryModel(**category.model_dump())
    db.add(db_category)
    await db.commit()
    await db.refresh(db_category)
    return db_category


@router.get("/{user_id}", name="Получить все категории", response_model=list[CategorySchema])
async def get_all_categories(user_id: int, db: AsyncSession = Depends(get_async_db)) -> list[CategorySchema]:
    user = await db.scalars(
        select(UserModel).where(UserModel.id == user_id, UserModel.is_active == True),  # noqa
    )
    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    result = await db.scalars(select(CategoryModel))
    categories = result.all()
    if not categories:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категории не найдены",
        )
    return categories


@router.put("/{category_id}", name="Обновить категорию", response_model=CategorySchema)
async def update_category(
    category_id: int,
    category: CategoryUpdateSchema,
    db: AsyncSession = Depends(get_async_db),
) -> CategorySchema:
    result = await db.scalars(
        select(CategoryModel).where(CategoryModel.id == category_id),
    )
    db_category = result.first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена",
        )
    await db.execute(
        update(CategoryModel).where(CategoryModel.id == category_id).values(**category.model_dump()),
    )
    await db.commit()
    await db.refresh(db_category)
    return db_category


@router.delete("/{category_id}", name="Удалить категорию", response_model=CategorySchema)
async def delete_category(category_id: int, db: AsyncSession = Depends(get_async_db)) -> CategorySchema:
    category = await db.scalars(
        select(CategoryModel).where(CategoryModel.id == category_id, CategoryModel.is_active == True),  # noqa
    )
    db_category = category.first()
    if not db_category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена",
        )
    db_category.is_active = False
    await db.commit()
    return db_category
