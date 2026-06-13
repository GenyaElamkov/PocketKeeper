from typing import List

from fastapi import APIRouter, Depends, status

from src.core.dependencies import get_account_service, get_current_member
from src.schemas.accounts import Account, AccountCreate, AccountUpdate
from src.schemas.users import User
from src.services.accounts import AccountService

router = APIRouter(
    prefix="/accounts",
    tags=["Счета пользователя"],
)


@router.get("/", name="Список счетов", response_model=List[Account])
async def get_all_accounts(
    account_service: AccountService = Depends(get_account_service),
    current_user: User = Depends(get_current_member),
) -> list[Account]:
    """Получение списка счетов пользователя."""
    return await account_service.get_accounts_by_user(current_user.id)


@router.post("/", name="Создать счет",
             response_model=Account,
             status_code=status.HTTP_201_CREATED)
async def create_account(
    account: AccountCreate,
    account_service: AccountService = Depends(get_account_service),
    current_user: User = Depends(get_current_member),
) -> Account:
    return await account_service.create_account(account.model_dump(), current_user.id)


@router.put("/{account_id}", name="Обновить счет", response_model=Account)
async def update_account(
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
        status_code=status.HTTP_200_OK)
async def delete_account(
    account_id: int,
    account_service: AccountService = Depends(get_account_service),
    current_user: User = Depends(get_current_member),
) -> Account:
    """Удаление счета."""
    return await account_service.delete_account(account_id, current_user.id)
