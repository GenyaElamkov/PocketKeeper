from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db_depends import get_async_db
from src.models.accounts import Account as AccountModel
from src.models.categories import Category as CategoryModel
from src.models.transactions import Transaction as TransactionModel
from src.models.users import User as UserModel
from src.schemas.transactions import Transaction as TransactionSchema
from src.schemas.transactions import \
    TransactionCreate as TransactionCreateSchema

router = APIRouter(
    prefix="/transactions",
    tags=["Транзакции"],
)


@router.post("/", name="Создать транзакцию", response_model=TransactionSchema, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: TransactionCreateSchema,
    db: AsyncSession = Depends(get_async_db),
) -> TransactionSchema:
    user = await db.scalars(
        select(UserModel).where(
            UserModel.id == transaction.user_id,
            UserModel.is_active == True,    # noqa
        ),
    )
    if not user.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден",
        )
    account = await db.scalars(
        select(AccountModel).where(
            AccountModel.id == transaction.account_id,
            AccountModel.is_archived == False,  # noqa
        ),
    )
    if not account.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Счет не найден",
        )

    category = await db.scalars(
        select(CategoryModel).where(
            CategoryModel.id == transaction.category_id,
            CategoryModel.is_active == True,    # noqa
        ),
    )
    if not category.first():
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена",
        )
    db_transaction = TransactionModel(**transaction.model_dump())
    db.add(db_transaction)
    await db.commit()
    await db.refresh(db_transaction)
    return db_transaction


@router.get("/", name="Список транзакций", response_model=list[TransactionSchema])
async def get_all_transactions(db: AsyncSession = Depends(get_async_db)) -> list[TransactionSchema]:
    transactions = await db.scalars(select(TransactionModel))
    db_transactions = transactions.all()
    if not db_transactions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Транзакции не найдены",
        )
    return db_transactions


@router.put("/{transaction_id}", name="Обновить транзакцию")
async def update_transaction(transaction_id: int) -> dict:
    return {"message": f"Транзакция с ID {transaction_id} обновлена (заглушка)"}


@router.delete("/{transaction_id}", name="Удалить транзакцию")
async def delete_transaction(transaction_id: int) -> dict:
    return {"message": f"Транзакция с ID {transaction_id} удалена (заглушка)"}
