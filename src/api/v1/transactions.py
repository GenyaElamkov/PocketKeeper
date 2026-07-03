from fastapi import APIRouter, Depends, Request, status

from src.core.dependencies import get_current_member, get_transaction_service
from src.infrastructure.infra_rate_limiter import limiter
from src.schemas.transactions import (Transaction, TransactionCreate,
                                      TransactionList, TransactionRequest,
                                      TransactionUpdate)
from src.schemas.users import User
from src.services.transactions import TransactionService

router = APIRouter(
    prefix="/transactions",
    tags=["Транзакции"],
)


@router.get("/", name="Список транзакций",
            response_model=TransactionList)
@limiter.limit("10/minute")
async def get_all_transactions(
    request: Request,
    transaction_request: TransactionRequest = Depends(),
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_member),
) -> TransactionList:
    """Список транзакций"""
    return await transaction_service.get_all(transaction_request, current_user.id)


@router.post("/", name="Создать транзакцию",
             response_model=Transaction,
             status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
async def create_transaction(
    request: Request,
    transaction: TransactionCreate,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_member),
) -> Transaction:
    """Создание транзакции"""
    return await transaction_service.create_transaction(transaction, current_user.id)


@router.put("/{transaction_id}", name="Обновить транзакцию", response_model=Transaction)
@limiter.limit("5/minute")
async def update_transaction(
    request: Request,
    transaction_id: int,
    update_data: TransactionUpdate,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_member),
) -> Transaction:
    """Обновление транзакции"""
    return await transaction_service.update_transaction(transaction_id, update_data, current_user.id)


@router.delete("/{transaction_id}",
               name="Удалить транзакцию",
               response_model=Transaction,
               status_code=status.HTTP_200_OK)
@limiter.limit("5/minute")
async def delete_transaction(
    request: Request,
    transaction_id: int,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_member),
) -> Transaction:
    """Удаление транзакции"""
    return await transaction_service.delete_transaction(transaction_id, current_user.id)
