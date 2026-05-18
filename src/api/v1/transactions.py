from fastapi import APIRouter, Depends, status

from src.core.dependencies import get_transaction_service
from src.models.users import User as UserModel
from src.schemas.transactions import Transaction as TransactionSchema
from src.schemas.transactions import \
    TransactionCreate as TransactionCreateSchema
from src.schemas.transactions import TransactionList as TransactionListSchema
from src.schemas.transactions import \
    TransactionRequest as TransactionRequestSchema
from src.schemas.transactions import \
    TransactionUpdate as TransactionUpdateSchema
from src.services.auth import get_current_member
from src.services.transactions import TransactionService

router = APIRouter(
    prefix="/transactions",
    tags=["Транзакции"],
)


@router.get("/", name="Список транзакций",
            response_model=TransactionListSchema)
async def get_all_transactions(
    request: TransactionRequestSchema = Depends(),
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: UserModel = Depends(get_current_member),
) -> TransactionListSchema:
    """Список транзакций"""
    return await transaction_service.get_all(request, current_user.id)


@router.post("/", name="Создать транзакцию",
             response_model=TransactionSchema,
             status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreateSchema,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: UserModel = Depends(get_current_member),
) -> TransactionSchema:
    """Создание транзакции"""
    return await transaction_service.create_transaction(transaction, current_user.id)


@router.put("/{transaction_id}", name="Обновить транзакцию", response_model=TransactionSchema)
async def update_transaction(
    transaction_id: int,
    update_data: TransactionUpdateSchema,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: UserModel = Depends(get_current_member),
) -> TransactionSchema:
    """Обновление транзакции"""
    return await transaction_service.update_transaction(transaction_id, update_data, current_user.id)


@router.delete("/{transaction_id}",
               name="Удалить транзакцию",
               response_model=TransactionSchema,
               status_code=status.HTTP_200_OK)
async def delete_transaction(
    transaction_id: int,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: UserModel = Depends(get_current_member),
) -> TransactionSchema:
    """Удаление транзакции"""
    return await transaction_service.delete_transaction(transaction_id, current_user.id)
