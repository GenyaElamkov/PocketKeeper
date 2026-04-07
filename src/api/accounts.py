from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db_depends import get_async_db
from src.auth import get_current_member
from src.models.accounts import Account as AccountModel
from src.models.users import User as UserModel
from src.schemas.accounts import Account as AccountSchema
from src.schemas.accounts import AccountsCreate as AccountsCreateSchema
from src.schemas.accounts import AccountUpdate as AccountUpdateSchema

router = APIRouter(
    prefix="/accounts",
    tags=["Счета пользователя"],
)


@router.post("/", name="Создать счет",
             response_model=AccountSchema, status_code=status.HTTP_201_CREATED)
async def create_account(account: AccountsCreateSchema,
                         db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_member),
                         ) -> AccountSchema:

    account_result = await db.scalars(
        select(AccountModel).where(
            AccountModel.name == account.name,
            AccountModel.user_id == current_user.id,
        ),
    )
    if account_result.first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Счет с таким именем уже существует",
        )
    db_account = AccountModel(**account.model_dump(), user_id=current_user.id)
    db.add(db_account)
    await db.commit()
    await db.refresh(db_account)
    return db_account


@router.get("/", name="Список счетов", response_model=list[AccountSchema])
async def get_all_accounts(db: AsyncSession = Depends(get_async_db),
                           current_user: UserModel = Depends(get_current_member),
                           ) -> list[AccountSchema]:

    accounts = await db.scalars(
        select(AccountModel).where(AccountModel.user_id == current_user.id),
    )
    db_accounts = accounts.all()
    if not db_accounts:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Счета не найдены",
        )
    return db_accounts


@router.put("/{account_id}", name="Обновить счет", response_model=AccountSchema)
async def update_account(account_id: int,
                         account: AccountUpdateSchema,
                         db: AsyncSession = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_member),
                         ) -> AccountSchema:
    result = await db.scalars(
        select(AccountModel).where(AccountModel.id == account_id),
    )
    db_account = result.first()
    if not db_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Счет не найден",
        )
    if db_account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления счета",
        )
    await db.execute(
        update(AccountModel).where(AccountModel.id == account_id).values(**account.model_dump()),
    )
    await db.commit()
    await db.refresh(db_account)
    return db_account


@router.delete("/{account_id}", name="Удалить счет", response_model=AccountSchema)
async def delete_account(account_id: int,
                         db: AccountSchema = Depends(get_async_db),
                         current_user: UserModel = Depends(get_current_member),
                         ) -> AccountSchema:
    result = await db.scalars(
        select(AccountModel).where(AccountModel.id == account_id),
    )
    db_account = result.first()
    if not db_account:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Счет не найден",
        )
    if db_account.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления счета",
        )
    db_account.is_archived = True
    await db.commit()
    await db.refresh(db_account)
    return db_account
