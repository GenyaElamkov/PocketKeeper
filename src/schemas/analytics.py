from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class AnalyticCategory(BaseModel):
    """Модель для аналитики по категориям"""
    category_id: int = Field(..., description="Индефикатор категории")
    total: Decimal = Field(..., description="Общая сумма")
    percentage: float = Field(..., description="Процент от общего")

    model_config = ConfigDict(from_attributes=True)


class AnalyticCategoryList(BaseModel):
    """Список по категориям"""
    items: list[AnalyticCategory] = Field(..., description="Список отчетов по категориям")

    model_config = ConfigDict(from_attributes=True)
