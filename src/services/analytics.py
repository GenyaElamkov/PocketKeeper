import calendar
from datetime import date
from decimal import Decimal
from uuid import UUID

from src.repositories.analytics import AnalyticRepository
from src.schemas.accounts import AccountCurrency
from src.schemas.analytics import (AnalyticCategoryList, AnalyticResponse,
                                   CategoryReport, PeriodInfo, PreviousPeriod,
                                   Totals)
from src.schemas.transactions import TransactionType
from src.services.analytics_helpers import (ZERO, CategoryInfo,
                                            build_category_tree,
                                            calc_change_pct, calc_percentage,
                                            calc_savings_rate, money,
                                            period_days,
                                            resolve_previous_period)


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
        start_date = date(year, month, 1)
        end_date = date(year, month, calendar.monthrange(year, month)[1])

        summary_data = await self.analytic_repo.get_total_category(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            transaction_type=transaction_type,
        )
        total_amount = self._get_total_amount(summary_data)
        for item in summary_data:
            item['percentage'] = calc_percentage(Decimal(item.get('total', 0)), total_amount)

        summary_data.sort(key=lambda x: x['percentage'], reverse=True)
        return AnalyticCategoryList(items=summary_data)

    async def get_summary_by_category(
            self,
            date_from: date,
            date_to: date,
            user_id: UUID,
            currency: AccountCurrency = AccountCurrency.RUB,
    ) -> AnalyticResponse:
        """Сводка доходов и расходов за период.

        Возвращает итоги, сравнение с предыдущим периодом и дерево категорий
        отдельно для расходов и доходов (сумма родителя включает вложенные категории).
        """
        currency_code = currency.value

        rows = await self.analytic_repo.get_totals_by_category(
            user_id=user_id,
            date_from=date_from,
            date_to=date_to,
            currency=currency_code,
        )
        categories = [
            CategoryInfo(
                category_id=row["id"], name=row["name"], parent_id=row["parent_id"], icon=row["icon"],
            )
            for row in await self.analytic_repo.get_categories(user_id)
        ]

        own_totals: dict[str, dict[int, Decimal]] = {
            TransactionType.expense.value: {},
            TransactionType.income.value: {},
        }
        for row in rows:
            bucket = own_totals.get(row["transaction_type"])
            if bucket is not None:
                bucket[row["category_id"]] = Decimal(row["total"])

        expense_total = sum(own_totals[TransactionType.expense.value].values(), ZERO)
        income_total = sum(own_totals[TransactionType.income.value].values(), ZERO)

        prev_from, prev_to, prev_type = resolve_previous_period(date_from, date_to)
        prev_totals = await self.analytic_repo.get_totals_by_type(
            user_id=user_id,
            date_from=prev_from,
            date_to=prev_to,
            currency=currency_code,
        )
        prev_expense = prev_totals.get(TransactionType.expense.value, ZERO)
        prev_income = prev_totals.get(TransactionType.income.value, ZERO)

        return AnalyticResponse(
            period=PeriodInfo(
                date_from=date_from,
                date_to=date_to,
                days=period_days(date_from, date_to),
            ),
            currency=currency,
            totals=Totals(
                income=money(income_total),
                expense=money(expense_total),
                balance=money(income_total - expense_total),
                savings_rate=calc_savings_rate(income_total, expense_total),
            ),
            previous_period=PreviousPeriod(
                date_from=prev_from,
                date_to=prev_to,
                prev_type=prev_type,
                income=money(prev_income),
                expense=money(prev_expense),
                income_change_pct=calc_change_pct(income_total, prev_income),
                expense_change_pct=calc_change_pct(expense_total, prev_expense),
            ),
            expense=CategoryReport(
                total=money(expense_total),
                items=build_category_tree(
                    own_totals[TransactionType.expense.value], categories, expense_total,
                ),
            ),
            income=CategoryReport(
                total=money(income_total),
                items=build_category_tree(
                    own_totals[TransactionType.income.value], categories, income_total,
                ),
            ),
        )

    @staticmethod
    def _get_total_amount(items: list[dict]) -> Decimal:
        """Вычислить общую сумму по списку элементов."""
        return sum((Decimal(item.get('total', 0)) for item in items), ZERO)
