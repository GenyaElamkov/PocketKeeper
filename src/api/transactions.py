import uuid

from fastapi import APIRouter

router = APIRouter(
    prefix="/transactions",
    tags=["Транзакции"],
)


@router.get("/", name="Список транзакций")
async def get_all_transactions() -> dict:
    return {"message": "Список всех транзакций (заглушка)"}


@router.post("/", name="Создать транзакцию")
async def create_transaction() -> dict:
    return {"message": "Транзакция создана (заглушка)"}


@router.put("/{transaction_id}", name="Обновить транзакцию")
async def update_transaction(transaction_id: uuid.UUID) -> dict:
    return {"message": f"Транзакция с ID {transaction_id} обновлена (заглушка)"}


@router.delete("/{transaction_id}", name="Удалить транзакцию")
async def delete_transaction(transaction_id: uuid.UUID) -> dict:
    return {"message": f"Транзакция с ID {transaction_id} удалена (заглушка)"}
