from datetime import date
from decimal import Decimal
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.categories import Category
from src.models.transactions import Transaction
from src.schemas.transactions import TransactionType


class AnalyticRepository:
    """Репозиторий для работы с отчетами."""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_total_category(
            self,
            user_id: UUID,
            start_date: date,
            end_date: date,
            transaction_type: TransactionType,
    ) -> list[dict]:
        """
        Получить общую сумму по категориям за период для одного типа транзакций.
        Возвращает список словарей с ключами: category_id, total.
        """
        filters = [
            Transaction.user_id == user_id,
            Transaction.transaction_type == transaction_type,
            Transaction.is_active.is_(True),
            Transaction.transaction_date.between(start_date, end_date),
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

    @staticmethod
    def _period_filters(
            user_id: UUID,
            date_from: date,
            date_to: date,
            currency: str,
    ) -> list:
        """Общие правила отбора транзакций для отчетов.

        Только активные транзакции пользователя за период (границы включительно),
        валюта определяется по счету. Переводы - отдельная сущность и сюда не попадают.
        """
        filters = [
            Transaction.user_id == user_id,
            Transaction.is_active.is_(True),
            Transaction.transaction_date.between(date_from, date_to),
            Account.currency == currency,
        ]
        return filters

    async def get_totals_by_category(
            self,
            user_id: UUID,
            date_from: date,
            date_to: date,
            currency: str,
    ) -> list[dict]:
        """Суммы по связке «тип транзакции + категория» за период.

        Возвращает список словарей: transaction_type, category_id, total.
        """
        result = await self.db.execute(
            select(
                Transaction.transaction_type.label("transaction_type"),
                Transaction.category_id.label("category_id"),
                func.sum(Transaction.amount).label("total"),
            )
            .join(Account, Transaction.account_id == Account.id)
            .where(*self._period_filters(user_id, date_from, date_to, currency))
            .group_by(Transaction.transaction_type, Transaction.category_id),
        )
        return [dict(row) for row in result.mappings().all()]

    async def get_totals_by_type(
            self,
            user_id: UUID,
            date_from: date,
            date_to: date,
            currency: str,
    ) -> dict[str, Decimal]:
        """Итоговые суммы по типам транзакций за период: {тип: сумма}."""
        result = await self.db.execute(
            select(
                Transaction.transaction_type,
                func.sum(Transaction.amount),
            )
            .join(Account, Transaction.account_id == Account.id)
            .where(*self._period_filters(user_id, date_from, date_to, currency))
            .group_by(Transaction.transaction_type),
        )
        return {row[0]: Decimal(row[1]) for row in result.all()}

    async def get_categories(self, user_id: UUID) -> list[dict]:
        """Все категории пользователя (включая неактивные) для построения дерева."""
        result = await self.db.execute(
            select(Category.id, Category.name, Category.parent_id, Category.icon)
            .where(Category.user_id == user_id),
        )
        return [dict(row) for row in result.mappings().all()]
