import calendar
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.categories import Category
from src.models.transactions import Transaction


class AnalyticRepository:
    """Репозиторий для работы с отчетами."""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def _get_total(
            self,
            user_id: int,
            start_date: date,
            end_date: date,
            transaction_type: str,
    ) -> float:
        """Получить общую сумму транзакций."""
        filters = [
            Transaction.user_id == user_id,
            Transaction.is_active.is_(True),
            Transaction.transaction_type == transaction_type,
            Transaction.transaction_date.between(start_date, end_date),

        ]
        return await self.db.scalar(
            select(func.sum(Transaction.amount)).filter(*filters),
        ) or 0.0

    async def get_total_month(
            self,
            user_id: int,
            month: int,
            year: int,
            transaction_type: str,
    ) -> float:
        """Получить общую сумму за месяц."""
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])

        return await self._get_total(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type,
        )

    async def get_total_year(
            self,
            user_id: int,
            year: int,
            transaction_type: str,
    ) -> float:
        """Получить общую сумму за год."""
        start_date = date(year, 1, 1)
        end_date = date(year, 12, calendar.monthrange(year, 12)[1])

        return await self._get_total(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type,
        )

    async def get_total_category(self, user_id: int, year: int, month:  int) -> list[dict]:
        """Получить общую сумму по категории."""
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])
        filters = [
            Transaction.user_id == user_id,
            Transaction.is_active.is_(True),
            Transaction.transaction_date.between(start_date, end_date),
        ]
        result = await self.db.execute(
            select(Category.name, func.coalesce(func.sum(Transaction.amount), 0.0))
            .join(Category, Transaction.category_id == Category.id)
            .filter(*filters)
            .group_by(Category.name),
        )
        return [dict(row) for row in result.mappings().all()]
