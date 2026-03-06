import uuid

from fastapi import APIRouter

router = APIRouter(
    prefix="/accounts",
    tags=["Счета пользователя"],
)


@router.get("/", name="Список счетов")
async def get_all_accounts() -> dict:
    return {"message": "Список всех счетов пользователя (заглушка)"}


@router.post("/", name="Создать счет")
async def create_account() -> dict:
    return {"message": "Счет создан (заглушка)"}


@router.put("/{account_id}", name="Обновить счет")
async def update_account(account_id: uuid.UUID) -> dict:
    return {"message": f"Счет с ID {account_id} обновлена (заглушка)"}


@router.delete("/{account_id}", name="Удалить счет")
async def delete_account(account_id: uuid.UUID) -> dict:
    return {"message": f"Счет с ID {account_id} удалена (заглушка)"}
