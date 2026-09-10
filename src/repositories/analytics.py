import calendar
from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.categories import Category
from src.models.transactions import Transaction
from src.schemas.transactions import TransactionType


class AnalyticRepository:
    """Репозиторий для работы с отчетами."""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_total_category(
            self,
            user_id: int,
            year: int,
            month:  int,
            transaction_type: TransactionType,
    ) -> list[dict]:
        """
        Получить общую сумму по категории.
        Возвращает список словарей с ключами: category, total.
        """
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])
        filters = [
            Transaction.user_id == user_id,
            Transaction.transaction_type == transaction_type,
            Transaction.is_active.is_(True),
            Transaction.transaction_date.between(start_date, end_date),
        ]
        result = await self.db.execute(
            select(
                Category.name.label("category"),
                func.coalesce(func.sum(Transaction.amount), 0.0).label("total"),
            )
            .join(Category, Transaction.category_id == Category.id)
            .filter(*filters)
            .group_by(Category.name),
        )
        return [dict(row) for row in result.mappings().all()]
