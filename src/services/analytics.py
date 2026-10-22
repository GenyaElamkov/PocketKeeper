import calendar
from datetime import date
from decimal import Decimal
from uuid import UUID

from src.repositories.analytics import AnalyticRepository
from src.schemas.analytics import AnalyticCategoryList, AnalyticResponse
from src.schemas.transactions import TransactionType
from src.services.analytics_helpers import ZERO, calc_percentage


class AnalyticService:
    """Сервис для работы с отчетами."""
    def __init__(
            self,
            analytic_repo: AnalyticRepository,
    ):
        self.analytic_repo = analytic_repo

    async def get_summary_for_month(
            self,
            month: int,
            year: int,
            transaction_type: TransactionType,
            user_id: UUID,
    ) -> AnalyticCategoryList:
        """
        Получить отчет по транзакциям за текущий месяц.
        Отчет формируется по категориям, итоговыми суммами и процентами
            category_id: int - Индефикатор категории
            total: Decimal - Общая сумма
            percentage: float = Процент от общей суммы
        """
        date_from = date(year, month, 1)
        date_to = date(year, month, calendar.monthrange(year, month)[1])

        summary_data = await self.analytic_repo.get_total_by_category(
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            transaction_type=transaction_type,
        )
        total_amount = self._get_total_amount(summary_data)
        for item in summary_data:
            item['percentage'] = calc_percentage(item.get('total', ZERO), total_amount)

        summary_data.sort(key=lambda x: x['percentage'], reverse=True)
        return AnalyticCategoryList(items=summary_data)

    async def get_summary_by_category(
            self,
            date_from: date,
            date_to: date,
            user_id: UUID,
    ) -> AnalyticResponse:
        """Сводка доходов и расходов за период.
        Возвращает итоги, сравнение с предыдущим периодом и дерево категорий
        отдельно для расходов и доходов (сумма родителя включает вложенные категории).
        """

        # Расход
        expense = await self.analytic_repo.get_total_by_category(
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            transaction_type=TransactionType.expense,
        )
        total_amount_expense = self._get_total_amount(expense)
        for item in expense:
            item['percentage'] = calc_percentage(item.get('total', ZERO), total_amount_expense)

        # Доход
        income = await self.analytic_repo.get_total_by_category(
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            transaction_type=TransactionType.income,
        )
        total_amount_income = self._get_total_amount(income)
        for item in income:
            item['percentage'] = calc_percentage(item.get('total', ZERO), total_amount_income)

        return AnalyticResponse(
            expense=AnalyticCategoryList(items=expense),
            income=AnalyticCategoryList(items=income),
        )

    @staticmethod
    def _get_total_amount(items: list[dict]) -> Decimal:
        """Вычислить общую сумму по списку элементов."""
        return sum((Decimal(item.get('total', ZERO)) for item in items), ZERO)
