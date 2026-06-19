from src.repositories.reports import ReportRepository
from src.schemas.reports import ReportRequest
from src.schemas.transactions import TransactionType


class ReportService:
    """Сервис для работы с отчетами."""
    def __init__(
            self,
            report_repo: ReportRepository,
    ):
        self.report_repo = report_repo

    async def get_monthly_summary(self, request: ReportRequest, user_id: int) -> dict:
        """Получить отчет по транзакциям."""
        total_income = await self.report_repo.get_total_month(
            user_id,
            request.month,
            request.year,
            TransactionType.income,
        )
        total_expense = await self.report_repo.get_total_month(
            user_id,
            request.month,
            request.year,
            TransactionType.expense,
        )

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - abs(total_expense),
        }

    async def get_yearly_summary(self, request: ReportRequest, user_id: int) -> dict:
        """Получить отчет по годам."""
        total_income = await self.report_repo.get_total_year(
            user_id,
            request.year,
            TransactionType.income,
        )
        total_expense = await self.report_repo.get_total_year(
            user_id,
            request.year,
            TransactionType.expense,
        )

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - abs(total_expense),
        }
