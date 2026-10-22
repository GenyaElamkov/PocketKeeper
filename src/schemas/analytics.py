from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field, model_validator


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


class AnalyticRequest(BaseModel):
    """Mодел запроса на получение статистических данных"""
    date_from: date = Field(..., description="Дата начала периода (в формате YYYY-MM-DD)")
    date_to: date = Field(..., description="Дата окончания периода (в формате YYYY-MM-DD)")

    @model_validator(mode="after")
    def validate_dates(self):
        if self.date_from > self.date_to:
            raise ValueError("Дата начала периода не может быть больше даты окончания периода")
        return self


class AnalyticResponse(BaseModel):
    """Модель ответа на запрос статистических данных"""
    expense: AnalyticCategoryList = Field(..., description="Отчет по расходам")
    income: AnalyticCategoryList = Field(..., description="Отчет по доходам")
