import uuid
from fastapi import APIRouter, status
from schemas.categories import CategoryCreate, Category


router = APIRouter(
    prefix="/categories",
    tags=["Категории"],
)


@router.get("/", name="Получить все категории", response_model=list[Category], status_code=status.HTTP_200_OK)
async def get_all_categories() -> list[Category]:
    return {"message": "Список всех категорий (загл ушка)"}


@router.post("/", name="Создать новую категорию", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(pyload: CategoryCreate) -> Category:
    return {"message": "Категория создана (заглушка)"}


@router.put("/{category_id}", name="Обновить категорию")
async def update_category(category_id: uuid.UUID) -> Category:
    return {"message": f"Категория с ID {category_id} обновлена (заглушка)"}


@router.delete("/{category_id}", name="Удалить категорию")
async def delete_category(category_id: uuid.UUID) -> dict:
    return {"message": f"Категория с ID {category_id} удалена (заглушка)"}


