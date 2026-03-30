from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db_depends import get_async_db
from src.models.accounts import Account as AccountModel
from src.models.users import User as UserModel
from src.schemas.accounts import Account as AccountSchema
from src.schemas.accounts import AccountsCreate as AccountsCreateSchema

router = APIRouter(
    prefix="/accounts",
    tags=["Счета пользователя"],
)


@router.post("/{user_id}", name="Создать счет", response_model=AccountSchema, status_code=status.HTTP_201_CREATED)
async def create_account(account: AccountsCreateSchema, db: AsyncSession = Depends(get_async_db)) -> AccountSchema:
    user = await db.scalars(
        select(UserModel).where(UserModel.id == account.user_id, UserModel.is_active == True),  # noqa
    )
    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )

    account_result = await db.scalars(
        select(AccountModel).where(
            AccountModel.name == account.name,
            AccountModel.user_id == account.user_id,
        ),
    )
    if account_result.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Счет с таким именем уже существует",
        )
    db_account = AccountModel(**account.model_dump())
    db.add(db_account)
    await db.commit()
    await db.refresh(db_account)
    return db_account


@router.get("/{user_id}", name="Список счетов", response_model=list[AccountSchema])
async def get_all_accounts(user_id: int, db: AsyncSession = Depends(get_async_db)) -> list[AccountSchema]:
    user = await db.scalars(
        select(UserModel).where(UserModel.id == user_id),
    )
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    accounts = await db.scalars(
        select(AccountModel).where(AccountModel.user_id == user_id, AccountModel.is_archived == False), # noqa
    )
    db_accounts = accounts.all()
    if not db_accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Счета не найдены",
        )
    return db_accounts


@router.put("/{account_id}", name="Обновить счет")
async def update_account(account_id: int) -> dict:
    return {"message": f"Счет с ID {account_id} обновлена (заглушка)"}


@router.delete("/{account_id}", name="Удалить счет")
async def delete_account(account_id: int) -> dict:
    return {"message": f"Счет с ID {account_id} удалена (заглушка)"}
