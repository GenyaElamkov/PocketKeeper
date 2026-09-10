from uuid import UUID

from src.repositories.analytics import AnalyticRepository
from src.schemas.analytics import AnalyticCategoryList
from src.schemas.transactions import TransactionType


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
            category: str - Категория
            total: Decimal - Общая сумма
            percentage: float = Процент от общей суммы
        """
        summary_data = await self.analytic_repo.get_total_category(
            user_id=user_id,
            month=month,
            year=year,
            transaction_type=transaction_type,
        )
        total_amount = sum(item.get('total', 0) for item in summary_data)
        for item in summary_data:
            item['percentage'] = round((item.get('total', 0) / total_amount * 100) if total_amount else 0.0)

        summary_data.sort(key=lambda x: x['percentage'], reverse=True)
        return AnalyticCategoryList(items=summary_data)
