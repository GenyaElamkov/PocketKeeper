from datetime import date
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.categories import Category
from src.models.transactions import Transaction
from src.schemas.transactions import TransactionType


class AnalyticRepository:
    """Репозиторий для работы с отчетами."""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_total_by_category(
            self,
            user_id: UUID,
            date_from: date,
            date_to: date,
            transaction_type: TransactionType,
    ) -> list[dict]:
        """
        Получить общую сумму по категории.
        Возвращает список словарей с ключами: category, total.
        Пример результата:
        {
            "items": [
                {
                    "category_id": 0,
                    "total": "0",
                }
            ]
        }
        """
        filters = [
            Transaction.user_id == user_id,
            Transaction.transaction_type == transaction_type,
            Transaction.is_active.is_(True),
            Transaction.transaction_date.between(date_from, date_to),
        ]
        result = await self.db.execute(
            select(
                Category.id.label("category_id"),
                func.coalesce(func.sum(Transaction.amount), 0.0).label("total"),
            )
            .join(Category, Transaction.category_id == Category.id)
            .filter(*filters)
            .group_by(Category.id),
        )
        return [dict(row) for row in result.mappings().all()]
