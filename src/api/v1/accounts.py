from typing import List

from fastapi import APIRouter, Depends, Request, status

from src.api.v1.docs.accounts import (CREATE_ACCOUNT_RESPONSES,
                                      DELETE_ACCOUNT_RESPONSES,
                                      GET_ALL_ACCOUNTS_RESPONSES,
                                      UPDATE_ACCOUNT_RESPONSES)
from src.core.dependencies import get_account_service, get_current_member
from src.infrastructure.infra_rate_limiter import limiter
from src.schemas.accounts import Account, AccountCreate, AccountUpdate
from src.schemas.users import User
from src.services.accounts import AccountService

router = APIRouter(
    prefix="/accounts",
    tags=["Счета пользователя"],
)


@router.get(
        "/",
        name="Список счетов",
        response_model=List[Account],
        summary='Получить список всех счетов текущего пользователя',
        description='Возвращает все активные счета, принадлежащие авторизованному пользователю.',
        response_description='Список счетов пользователя',
        responses=GET_ALL_ACCOUNTS_RESPONSES,
)
@limiter.limit("10/minute")
async def get_all_accounts(
    request: Request,
    account_service: AccountService = Depends(get_account_service),
    current_user: User = Depends(get_current_member),
) -> list[Account]:
    """Получение списка счетов пользователя."""
    return await account_service.get_accounts_by_user(current_user.id)


@router.post(
        "/",
        name="Создать счет",
        response_model=Account,
        status_code=status.HTTP_201_CREATED,
        summary="Создать новый счёт",
        description="Создаёт новый счёт для текущего пользователя. Начальный баланс становится текущим балансом.",
        response_description="Данные созданного счёта",
        responses=CREATE_ACCOUNT_RESPONSES,
)
@limiter.limit("5/minute")
async def create_account(
    request: Request,
    account: AccountCreate,
    account_service: AccountService = Depends(get_account_service),
    current_user: User = Depends(get_current_member),
) -> Account:
    return await account_service.create_account(account.model_dump(), current_user.id)


@router.put(
        "/{account_id}",
        name="Обновить счет",
        response_model=Account,
        summary="Обновить существующий счёт",
        description="Изменяет название и/или начальный баланс счёта. "
                "Если по счёту уже есть транзакции, изменить начальный баланс нельзя.",
        response_description="Обновлённые данные счёта",
        responses=UPDATE_ACCOUNT_RESPONSES,
)
@limiter.limit("5/minute")
async def update_account(
    request: Request,
    account_id: int,
    account: AccountUpdate,
    account_service: AccountService = Depends(get_account_service),
    current_user: User = Depends(get_current_member),
) -> Account:
    """Обновление счета."""
    return await account_service.update_account(account_id, account.model_dump(), current_user.id)


@router.delete(
        "/{account_id}",
        name="Удалить счет",
        response_model=Account,
        status_code=status.HTTP_200_OK,
        summary="Удалить (архивировать) счёт",
        description="Удаляет счёт (мягкое удаление). Доступно только для владельца счёта.",
        response_description="Данные удалённого (архивированного) счёта",
        responses=DELETE_ACCOUNT_RESPONSES,
)
@limiter.limit("5/minute")
async def delete_account(
    request: Request,
    account_id: int,
    account_service: AccountService = Depends(get_account_service),
    current_user: User = Depends(get_current_member),
) -> Account:
    """Удаление счета."""
    return await account_service.delete_account(account_id, current_user.id)
