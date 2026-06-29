from fastapi import APIRouter, Depends

from src.core.dependencies import get_analytic_service, get_current_member
from src.schemas.analytics import (Analytic, AnalyticCategoryList,
                                   AnalyticRequest, AnalyticYearlyRequest)
from src.schemas.users import User
from src.services.analytics import AnalyticService

router = APIRouter(
    prefix="/analytics",
    tags=["Отчеты"],
)


@router.get("/monthly-summary", name="Отчет за месяц", response_model=Analytic)
async def get_analytics_monthly_summary(
    request: AnalyticRequest = Depends(),
    analytics_service: AnalyticService = Depends(get_analytic_service),
    current_user: User = Depends(get_current_member),

) -> Analytic:
    """Получение данных за месяц."""
    return await analytics_service.get_monthly_summary(request, current_user.id)


@router.get("/yearly-summary", name="Отчет за год", response_model=Analytic)
async def get_analytics_yearly_summary(
    request: AnalyticYearlyRequest = Depends(),
    analytics_service: AnalyticService = Depends(get_analytic_service),
    current_user: User = Depends(get_current_member),
) -> Analytic:
    """Получение данных за год."""
    return await analytics_service.get_yearly_summary(request, current_user.id)


@router.get("/category", name="Отчет по категориям", deprecated=True)
async def get_analytics_category(
    request: AnalyticRequest = Depends(),
    analytics_service: AnalyticService = Depends(get_analytic_service),
    current_user: User = Depends(get_current_member),
) -> AnalyticCategoryList:
    """Получение данных по категориям - сумма и процент."""
    return await analytics_service.get_category_summary(request, current_user.id)
