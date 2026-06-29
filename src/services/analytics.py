from src.repositories.analytics import AnalyticRepository
from src.schemas.analytics import (Analytic, AnalyticCategoryList,
                                   AnalyticRequest, AnalyticYearlyRequest)
from src.schemas.transactions import TransactionType


class AnalyticService:
    """Сервис для работы с отчетами."""
    def __init__(
            self,
            analytic_repo: AnalyticRepository,
    ):
        self.analytic_repo = analytic_repo

    async def get_monthly_summary(self, request: AnalyticRequest, user_id: int) -> Analytic:
        """Получить отчет по транзакциям."""
        total_income = await self.analytic_repo.get_total_month(
            user_id,
            request.month,
            request.year,
            TransactionType.income,
        )
        total_expense = await self.analytic_repo.get_total_month(
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

    async def get_yearly_summary(self, request: AnalyticYearlyRequest, user_id: int) -> Analytic:
        """Получить отчет по годам."""
        total_income = await self.analytic_repo.get_total_year(
            user_id,
            request.year,
            TransactionType.income,
        )
        total_expense = await self.analytic_repo.get_total_year(
            user_id,
            request.year,
            TransactionType.expense,
        )

        return {
            "total_income": total_income,
            "total_expense": total_expense,
            "balance": total_income - abs(total_expense),
        }

    async def get_category_summary(self, request: AnalyticRequest, user_id: int) -> AnalyticCategoryList:
        """Получить отчет по категориям."""
