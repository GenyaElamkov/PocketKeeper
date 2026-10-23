from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query

from src.api.v1.docs.analytics import GET_CURRENT_USER_RESPONSES
from src.core.dependencies import get_analytic_service, get_current_member
from src.schemas.analytics import (AnalyticCategoryList, AnalyticRequest,
                                   AnalyticResponse)
from src.schemas.transactions import TransactionType
from src.schemas.users import User
from src.services.analytics import AnalyticService

router = APIRouter(
    prefix="/analytics",
    tags=["Отчеты"],
)


@router.get(
        "/monthly-summary-by-category",
        name="Отчет за месяц по категориям",
        response_model=AnalyticCategoryList,
        summary="Статистика траты",
        description="Сводка расходов и дохода в разрезе каждой из существующих категории",
        response_description="Список с данными о сумме транзакций",
        responses=GET_CURRENT_USER_RESPONSES,
)
async def get_summary_by_category_for_current_month(
    analytics_service: AnalyticService = Depends(get_analytic_service),
    current_user: User = Depends(get_current_member),
) -> AnalyticCategoryList:
    """Получение данных за текущий месяц по категориям (расходы)."""
    return await analytics_service.get_summary_for_month(
        month=date.today().month,
        year=date.today().year,
        transaction_type=TransactionType.expense,
        user_id=current_user.id,
    )


@router.get(
        "/summary-income-expense",
        name='Общая статистика доходов и расходов',
        response_model=AnalyticResponse,
        summary="Доход - Расход",
        description=(
            "Итоги доходов и расходов за период, сравнение с предыдущим периодом "
            "и разбивка по категориям с учетом вложенности"
        ),
        response_description="Итоги, сравнение с предыдущим периодом и категории",
        responses=GET_CURRENT_USER_RESPONSES,
)
async def get_summary_by_category_for_period(
    analytic_request: Annotated[AnalyticRequest, Query()],
    analytics_service: AnalyticService = Depends(get_analytic_service),
    current_user: User = Depends(get_current_member),
) -> AnalyticResponse:
    """Получить итоги и разбивку по категориям за период."""
    return await analytics_service.get_summary_by_category(
        date_from=analytic_request.date_from,
        date_to=analytic_request.date_to,
        user_id=current_user.id,
        currency=analytic_request.currency,
    )
