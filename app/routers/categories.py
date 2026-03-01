import uuid
from fastapi import APIRouter


router = APIRouter(
    prefix="/categories",
    tags=["Категории"],
)


@router.get("/", name="Получить все категории")
async def get_all_categories() -> dict:
    return {"message": "Список всех категорий (заглушка)"}


@router.post("/", name="Создать новую категорию")
async def create_category() -> dict:
    return {"message": "Категория создана (заглушка)"}


@router.put("/{category_id}", name="Обновить категорию")
async def update_category(category_id: uuid.UUID) -> dict:
    return {"message": f"Категория с ID {category_id} обновлена (заглушка)"}


@router.delete("/{category_id}", name="Удалить категорию")
async def delete_category(category_id: uuid.UUID) -> dict:
    return {"message": f"Категория с ID {category_id} удалена (заглушка)"}

