from fastapi import APIRouter, Depends

from src.core.dependencies import get_current_member, get_report_service
from src.schemas.reports import Report, ReportRequest, ReportYearlyRequest
from src.schemas.users import User
from src.services.reports import ReportService

router = APIRouter(
    prefix="/reports",
    tags=["Отчеты"],
)


@router.get("/monthly-summary", name="Отчет за месяц", response_model=Report)
async def get_reports_monthly_summary(
    request: ReportRequest = Depends(),
    report_service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_member),

) -> Report:
    """Получение отчетов за месяц."""
    return await report_service.get_monthly_summary(request, current_user.id)


@router.get("/yearly-summary", name="Отчет за год", response_model=Report)
async def get_reports_yearly_summary(
    request: ReportYearlyRequest = Depends(),
    report_service: ReportService = Depends(get_report_service),
    current_user: User = Depends(get_current_member),
) -> Report:
    """Получение отчетов за год."""
    return await report_service.get_yearly_summary(request, current_user.id)


@router.get("/category", name="Отсчет по категориям")
async def get_reports_category(
    current_user: User = Depends(get_current_member),
):
    """Получение отчетов по категориям - сумма и процент."""
