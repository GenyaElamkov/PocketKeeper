import uuid
from fastapi import APIRouter


router = APIRouter(
    prefix="/users",
    tags=["Пользователи"],
)


@router.get("/", name="Список пользователей")
async def get_all_users() -> dict:
    return {"message": "Список всех пользователей (заглушка)"}


@router.post("/", name="Создать пользователя")
async def create_user() -> dict:
    return {"message": "Пользователь создана (заглушка)"}


@router.put("/{user_id}", name="Обновить пользователя")
async def update_user(user_id: uuid.UUID) -> dict:
    return {"message": f"User с ID {user_id} обновлена (заглушка)"}


@router.delete("/{user_id}", name="Удалить пользователя")
async def delete_user(user_id: uuid.UUID) -> dict:
    return {"message": f"Пользователь с ID {user_id} удалена (заглушка)"}

