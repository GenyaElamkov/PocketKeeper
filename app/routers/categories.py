import uuid
from fastapi import APIRouter, status
from schemas.categories import CategoryCreate, Category
from models.categories import categories_bd 


router = APIRouter(
    prefix="/categories",
    tags=["Категории"],
)


@router.get("/", name="Получить все категории", response_model=list[Category], status_code=status.HTTP_200_OK)
async def get_all_categories() -> list[Category]:
    # return {"message": "Список всех категорий (загл ушка)"}
    return categories_bd


@router.post("/", name="Создать новую категорию", response_model=Category, status_code=status.HTTP_201_CREATED)
async def create_category(pyload: CategoryCreate) -> Category:
    # return {"message": "Категория создана (заглушка)"}
    new_id = uuid.uuid4()
    category = {
        "id": new_id,
        "name": pyload.name,
        "icon": pyload.icon,
        "parent_id": pyload.parent_id,
    }
    categories_bd.append(category)
    return category


@router.put("/{category_id}", name="Обновить категорию")
async def update_category(category_id: uuid.UUID) -> Category:
    return {"message": f"Категория с ID {category_id} обновлена (заглушка)"}


@router.delete("/{category_id}", name="Удалить категорию")
async def delete_category(category_id: uuid.UUID) -> dict:
    return {"message": f"Категория с ID {category_id} удалена (заглушка)"}


