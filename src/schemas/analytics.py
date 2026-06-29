from pydantic import BaseModel, Field


class Analytic(BaseModel):
    """Модель для аналитики"""
    total_income: float = Field(..., description="Общий доход")
    total_expense: float = Field(..., description="Общий расход")
    balance: float = Field(..., description="Остаток")


class AnalyticRequest(BaseModel):
    """Модель для аналитики ввода"""
    month: int | None = Field(None, description="Месяц")
    year: int | None = Field(None, description="Год")


class AnalyticYearlyRequest(BaseModel):
    """Модель для аналитики за определенный год"""
    year: int = Field(..., description="Год")


class AnalyticCategory(BaseModel):
    """Модель для аналитики по категориям"""
    category: str = Field(..., description="Категория")
    total: float = Field(..., description="Общая сумма")
    precent: float = Field(..., description="Процент от общего")


class AnalyticCategoryList(BaseModel):
    """Список по категориям"""
    items: list[AnalyticCategory] = Field(..., description="Список отчетов по категориям")
