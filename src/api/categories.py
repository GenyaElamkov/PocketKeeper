import uuid

from fastapi import APIRouter, status

router = APIRouter(
    prefix="/categories",
    tags=["Категории"],
)


@router.get("/", name="Получить все категории", status_code=status.HTTP_200_OK)
async def get_all_categories():
    return {"message": "Список всех категорий (заглушка)"}


@router.post("/", name="Создать новую категорию", status_code=status.HTTP_201_CREATED)
async def create_category():
    return {"message": "Категория создана (заглушка)"}


@router.put("/{category_id}", name="Обновить категорию")
async def update_category(category_id: uuid.UUID):
    return {"message": f"Категория с ID {category_id} обновлена (заглушка)"}


@router.delete("/{category_id}", name="Удалить категорию")
async def delete_category(category_id: uuid.UUID) -> dict:
    return {"message": f"Категория с ID {category_id} удалена (заглушка)"}
