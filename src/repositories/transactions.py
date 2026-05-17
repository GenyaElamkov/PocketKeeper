from collections.abc import Sequence
from datetime import date
from typing import Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.transactions import Transaction


class TransactionRepository:
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
            .order_by(Transaction.transaction_date.desc())
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = (await self.db.scalars(transaction_stmt)).all()
        return items, total
