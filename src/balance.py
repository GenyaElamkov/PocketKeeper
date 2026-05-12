from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account as AccountModel
from src.models.transactions import Transaction as TransactionModel
from src.schemas.transactions import TransactionType


async def update_account_balance(db: AsyncSession, account_id: int):
    """Обновляет баланс счета."""
    balance_delta = case(
        (TransactionModel.type == TransactionType.income, TransactionModel.amount),
        (TransactionModel.type == TransactionType.expense, -TransactionModel.amount),
        else_=0,
    )

    result = await db.execute(
        select(func.sum(balance_delta)).where(
            TransactionModel.account_id == account_id,
            TransactionModel.is_active.is_(True),
        ),
    )
    transactions_sum = result.scalar() or 0.0
    account = await db.get(AccountModel, account_id)

    account.balance = account.initial_balance + transactions_sum
    await db.commit()
