from decimal import Decimal

from sqlalchemy import case, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.transactions import Transaction
from src.models.transfers import Transfer
from src.schemas.transactions import TransactionType


class BalanceRepository:
    """Репозиторий отвечает за пересчет баланса счета."""
    def __init__(self, db=AsyncSession):
        self.db = db

    async def recalculate(self, account_id: int) -> None:
        """Пересчитать баланс счёта: initial_balance + транзакции + переводы."""
        balance_delta = case(
            (Transaction.transaction_type == TransactionType.income, Transaction.amount),
            (Transaction.transaction_type == TransactionType.expense, -Transaction.amount),
            else_=0,
        )
        # Cумма транзакций.
        tx_sum = await self.db.execute(
            select(func.sum(balance_delta)).where(
                Transaction.account_id == account_id,
                Transaction.is_active.is_(True),
            ),
        )
        transactions_sum = tx_sum.scalar() or Decimal(0)

        # Cумма входящих переводов.
        inc_sum = await self.db.execute(
            select(func.sum(Transfer.amount)).where(
                Transfer.to_account_id == account_id,
                Transfer.is_active.is_(True),
            ),
        )
        incoming_sum = inc_sum.scalar() or Decimal(0)

        # Cумма исходящих переводов.
        out_sum = await self.db.execute(
            select(func.sum(Transfer.amount)).where(
                Transfer.from_account_id == account_id,
                Transfer.is_active.is_(True),
            ),
        )
        outgoing_sum = out_sum.scalar() or Decimal(0)

        account = await self.db.get(Account, account_id)
        account.balance = account.initial_balance + transactions_sum + incoming_sum - outgoing_sum
        await self.db.commit()
