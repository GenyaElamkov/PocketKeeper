from fastapi import APIRouter, Depends, status

from src.core.dependencies import get_transaction_service
from src.models.users import User as UserModel
from src.schemas.transactions import (Transaction, TransactionCreate,
                                      TransactionList, TransactionRequest,
                                      TransactionUpdate)
from src.services.current import get_current_member
from src.services.transactions import TransactionService

router = APIRouter(
    prefix="/transactions",
    tags=["Транзакции"],
)


@router.get("/", name="Список транзакций",
            response_model=TransactionList)
async def get_all_transactions(
    request: TransactionRequest = Depends(),
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: UserModel = Depends(get_current_member),
) -> TransactionList:
    """Список транзакций"""
    return await transaction_service.get_all(request, current_user.id)


@router.post("/", name="Создать транзакцию",
             response_model=Transaction,
             status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreate,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: UserModel = Depends(get_current_member),
) -> Transaction:
    """Создание транзакции"""
    return await transaction_service.create_transaction(transaction, current_user.id)


@router.put("/{transaction_id}", name="Обновить транзакцию", response_model=Transaction)
async def update_transaction(
    transaction_id: int,
    update_data: TransactionUpdate,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: UserModel = Depends(get_current_member),
) -> Transaction:
    """Обновление транзакции"""
    return await transaction_service.update_transaction(transaction_id, update_data, current_user.id)


@router.delete("/{transaction_id}",
               name="Удалить транзакцию",
               response_model=Transaction,
               status_code=status.HTTP_200_OK)
async def delete_transaction(
    transaction_id: int,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: UserModel = Depends(get_current_member),
) -> Transaction:
    """Удаление транзакции"""
    return await transaction_service.delete_transaction(transaction_id, current_user.id)
