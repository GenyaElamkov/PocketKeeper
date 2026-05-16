from typing import List

from fastapi import APIRouter, Depends, status

from src.core.dependencies import get_account_service
from src.models.users import User as UserModel
from src.schemas.accounts import Account as AccountSchema
from src.schemas.accounts import AccountCreate as AccountCreateSchema
from src.schemas.accounts import AccountUpdate as AccountUpdateSchema
from src.services.accounts import AccountService
from src.services.auth import get_current_member

router = APIRouter(
    prefix="/accounts",
    tags=["Счета пользователя"],
)


@router.get("/", name="Список счетов", response_model=List[AccountSchema])
async def get_all_accounts(
    account_service: AccountService = Depends(get_account_service),
    current_user: UserModel = Depends(get_current_member),
) -> list[AccountSchema]:
    """Получение списка счетов пользователя."""
    return await account_service.get_accounts_by_user(current_user.id)


@router.post("/", name="Создать счет",
             response_model=AccountSchema,
             status_code=status.HTTP_201_CREATED)
async def create_account(
    account: AccountCreateSchema,
    account_service: AccountService = Depends(get_account_service),
    current_user: UserModel = Depends(get_current_member),
) -> AccountSchema:
    return await account_service.create_account(account.model_dump(), current_user.id)


@router.put("/{account_id}", name="Обновить счет", response_model=AccountSchema)
async def update_account(
    account_id: int,
    account: AccountUpdateSchema,
    account_service: AccountService = Depends(get_account_service),
    current_user: UserModel = Depends(get_current_member),
) -> AccountSchema:
    """Обновление счета."""
    return await account_service.update_account(account_id, account, current_user.id)


@router.delete("/{account_id}", name="Удалить счет", response_model=AccountSchema)
async def delete_account(
    account_id: int,
    account_service: AccountService = Depends(get_account_service),
    current_user: UserModel = Depends(get_current_member),
) -> AccountSchema:
    """Удаление счета."""
    return await account_service.delete_account(account_id, current_user.id)
