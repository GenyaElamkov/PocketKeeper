from pydantic import BaseModel, ConfigDict, Field


class Report(BaseModel):
    """Модель для отчёта"""
    total_income: float = Field(..., description="Общий доход")
    total_expense: float = Field(..., description="Общий расход")
    balance: float = Field(..., description="Остаток")


class ReportList(BaseModel):
    """Модель для списка отчётов"""
    items: list[Report] = Field(..., description="Список отчётов")
    total: int = Field(ge=0, description="Общее количество отчётов")
    page: int = Field(ge=1, description="Номер страницы")
    page_size: int = Field(ge=15, description="Количество элементов на странице")

    model_config = ConfigDict(from_attributes=True)


class ReportRequest(BaseModel):
    """Модель для отчётов"""
    month: int | None = Field(None, description="Месяц")
    year: int | None = Field(None, description="Год")


class ReportYearlyRequest(BaseModel):
    """Модель для отчётов за определенный год"""
    year: int = Field(..., description="Год")
