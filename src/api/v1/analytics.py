from datetime import date

from fastapi import APIRouter, Depends

from src.core.dependencies import get_analytic_service, get_current_member
from src.schemas.analytics import AnalyticCategoryList
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
