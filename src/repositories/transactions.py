from collections.abc import Sequence
from datetime import date
from typing import Optional

from sqlalchemy import case, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.transactions import Transaction
from src.schemas.transactions import TransactionType


class TransactionRepository:
    """Репозиторий для работы с транзакциями."""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_filtered(
        self,
        user_id: int,
        page: int,
        page_size: int,
        transaction_date: Optional[date] = None,
        category_id: Optional[int] = None,
        account_id: Optional[int] = None,
    ) -> tuple[Sequence[Transaction], int]:
        """Получить все транзакции пользователя."""
        filters = [
            Transaction.user_id == user_id,
            Transaction.is_active.is_(True),
        ]
        if transaction_date:
            filters.append(Transaction.transaction_date == transaction_date)
        if category_id:
            filters.append(Transaction.category_id == category_id)
        if account_id:
            filters.append(Transaction.account_id == account_id)

        total_stmt = select(func.count()).select_from(Transaction).where(*filters)
        total = await self.db.scalar(total_stmt) or 0
        transaction_stmt = (
            select(Transaction)
            .where(*filters)
            .order_by(Transaction.transaction_date.desc(), Transaction.id.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = (await self.db.scalars(transaction_stmt)).all()
        return items, total

    async def create(self, transaction: dict, user_id: int) -> Transaction:
        """Создать транзакцию."""
        db_transaction = Transaction(**transaction, user_id=user_id)
        self.db.add(db_transaction)
        await self.db.flush()
        await self.db.refresh(db_transaction)
        return db_transaction

    async def update_account_balance(self, account_id: int) -> None:
        """Обновить баланс счета."""
        balance_delta = case(
            (Transaction.transaction_type == TransactionType.income, Transaction.amount),
            (Transaction.transaction_type == TransactionType.expense, -Transaction.amount),
            else_=0,
        )

        result = await self.db.execute(
            select(func.sum(balance_delta)).where(
                Transaction.account_id == account_id,
                Transaction.is_active.is_(True),
            ),
        )
        transactions_sum = result.scalar() or 0.0
        account = await self.db.get(Account, account_id)

        account.balance = account.initial_balance + transactions_sum
        await self.db.commit()

    async def update(self, transaction_id: int, data: dict) -> None:
        """Обновить транзакцию."""
        await self.db.execute(
            update(Transaction)
            .where(Transaction.id == transaction_id)
            .values(**data),
        )
        await self.db.flush()

    async def get_active_transaction_by_id(self, transaction_id: int) -> Transaction | None:
        """Проверить, существует ли активная транзакция с указанным ID."""
        filters = [
            Transaction.id == transaction_id,
            Transaction.is_active.is_(True),
        ]
        return await self.db.scalar(select(Transaction).filter(*filters))

    async def transaction_exists(self, account_id: int) -> bool:
        """Проверить, существует ли транзакция по Account.id с указанным ID."""
        filters = [
            Transaction.account_id == account_id,
            Transaction.is_active.is_(True),

        ]
        return await self.db.scalar(select(Transaction).filter(*filters)) is not None

    async def delete(self, delete_transaction: Transaction) -> None:
        """Мягко удалить транзакцию."""
        delete_transaction.is_active = False
        await self.db.flush()
