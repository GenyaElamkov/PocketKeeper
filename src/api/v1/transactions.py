from fastapi import APIRouter, Depends, Request, status

from src.api.v1.docs.transactions import (CREATE_TRANSACTION_RESPONSES,
                                          DELETE_TRANSACTION_RESPONSES,
                                          GET_ALL_TRANSACTIONS_RESPONSES,
                                          UPDATE_TRANSACTIONS_RESPONSES)
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


@router.get(
        "/",
        name="Список транзакций",
        response_model=TransactionList,
        summary="Получить список транзакций с фильтрацией и пагинацией",
        description="""
        Возвращает список транзакций текущего пользователя с поддержкой:

        - **Пагинация**: `page` (по умолчанию 1), `page_size` (по умолчанию 20)
        - **Фильтрация по дате**: `date_from`, `date_to` (ISO-формат)
        - **Фильтрация по категории**: `category_id`
        - **Фильтрация по счёту**: `account_id`
        - **Фильтрация по типу**: `transaction_type` (`income` / `expense` / `transfer`)
        - **Сортировка по дате**: `date_sort` (`asc` / `desc`, по умолчанию `desc`)
        """,
        response_description="Список транзакций с пагинацией и общим количеством",
        responses=GET_ALL_TRANSACTIONS_RESPONSES,
)
@limiter.limit("10/minute")
async def get_all_transactions(
    request: Request,
    transaction_request: TransactionRequest = Depends(),
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_member),
) -> TransactionList:
    """Список транзакций"""
    return await transaction_service.get_all(transaction_request, current_user.id)


@router.post(
        "/",
        name="Создать транзакцию",
        response_model=Transaction,
        status_code=status.HTTP_201_CREATED,
        summary="Создать новую транзакцию",
        description="""
        Создаёт новую транзакцию (доход, расход или перевод).

        - **Для дохода/расхода**: указывается `account_id`, `category_id`, сумма, дата, описание.

        Баланс счёта автоматически обновляется.
        """,
        response_description="Данные созданной транзакции",
        responses=CREATE_TRANSACTION_RESPONSES,
)
@limiter.limit("5/minute")
async def create_transaction(
    request: Request,
    transaction: TransactionCreate,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_member),
) -> Transaction:
    """Создание транзакции"""
    return await transaction_service.create_transaction(transaction, current_user.id)


@router.put(
        "/{transaction_id}",
        name="Обновить транзакцию",
        response_model=Transaction,
        summary="Обновить существующую транзакцию",
        description="""
        Изменяет параметры транзакции: сумму, категорию, счёт, дату, описание.

        При изменении счёта или суммы баланс автоматически пересчитывается для обоих счетов
        (если меняется счёт, то старый и новый счета пересчитываются).
        """,
        response_description="Обновлённые данные транзакции",
        responses=UPDATE_TRANSACTIONS_RESPONSES,
)
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


@router.delete(
        "/{transaction_id}",
        name="Удалить транзакцию",
        response_model=Transaction,
        status_code=status.HTTP_200_OK,
        summary="Удалить транзакцию (возврат баланса)",
        description="""
        Удаляет транзакцию и автоматически возвращает баланс счёта в исходное состояние.
        После удаления транзакция помечается как неактивная (soft delete).
        """,
        response_description="Данные удалённой транзакции",
        responses=DELETE_TRANSACTION_RESPONSES,
)
@limiter.limit("5/minute")
async def delete_transaction(
    request: Request,
    transaction_id: int,
    transaction_service: TransactionService = Depends(get_transaction_service),
    current_user: User = Depends(get_current_member),
) -> Transaction:
    """Удаление транзакции"""
    return await transaction_service.delete_transaction(transaction_id, current_user.id)
