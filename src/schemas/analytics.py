from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator

from src.schemas.accounts import AccountCurrency


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
    """Модель запроса на получение статистических данных"""
    date_from: date = Field(..., description="Дата начала периода (в формате YYYY-MM-DD)")
    date_to: date = Field(..., description="Дата окончания периода (в формате YYYY-MM-DD)")
    currency: AccountCurrency = Field(
        AccountCurrency.RUB,
        description="Валюта счетов, по которым строится отчет (пересчета между валютами нет)",
    )

    @model_validator(mode="after")
    def validate_dates(self):
        if self.date_from > self.date_to:
            raise ValueError("Дата начала периода не может быть больше даты окончания периода")
        return self


class PreviousPeriodType(str, Enum):
    """Как выбран предыдущий период для сравнения"""
    calendar_month = "calendar_month"
    same_days_previous_month = "same_days_previous_month"
    same_length = "same_length"


class PeriodInfo(BaseModel):
    """Границы выбранного периода"""
    date_from: date = Field(..., description="Начало периода")
    date_to: date = Field(..., description="Конец периода (включительно)")
    days: int = Field(..., description="Количество дней в периоде (включительно)")


class Totals(BaseModel):
    """Итоги за период"""
    income: Decimal = Field(..., description="Всего доходов")
    expense: Decimal = Field(..., description="Всего расходов")
    balance: Decimal = Field(..., description="Доходы минус расходы")
    savings_rate: float | None = Field(
        None,
        description="Норма сбережений в % от доходов; null, если доходов нет",
    )


class PreviousPeriod(BaseModel):
    """Предыдущий период и сравнение с ним"""
    date_from: date = Field(..., description="Начало предыдущего периода")
    date_to: date = Field(..., description="Конец предыдущего периода (включительно)")
    prev_type: PreviousPeriodType = Field(..., description="Способ выбора предыдущего периода")
    income: Decimal = Field(..., description="Доходы за предыдущий период")
    expense: Decimal = Field(..., description="Расходы за предыдущий период")
    income_change_pct: float | None = Field(
        None, description="Изменение доходов в %, null если в предыдущем периоде их не было",
    )
    expense_change_pct: float | None = Field(
        None, description="Изменение расходов в %, null если в предыдущем периоде их не было",
    )


class CategoryNode(BaseModel):
    """Категория с суммой (с учетом вложенных категорий) и дочерними узлами"""
    category_id: int = Field(..., description="Идентификатор категории")
    name: str = Field(..., description="Название категории")
    icon: str | None = Field(None, description="Иконка (эмодзи) категории")
    total: Decimal = Field(..., description="Сумма по категории вместе со вложенными")
    percentage: float = Field(..., description="Доля от общей суммы своего типа (расходы/доходы)")
    children: list["CategoryNode"] = Field(default_factory=list, description="Вложенные категории")


class CategoryReport(BaseModel):
    """Отчет по одному типу транзакций (расходы или доходы)"""
    total: Decimal = Field(..., description="Общая сумма по типу")
    items: list[CategoryNode] = Field(..., description="Категории верхнего уровня")


class AnalyticResponse(BaseModel):
    """Модель ответа на запрос статистических данных"""
    period: PeriodInfo = Field(..., description="Выбранный период")
    currency: AccountCurrency = Field(..., description="Валюта отчета")
    totals: Totals = Field(..., description="Итоги за период")
    previous_period: PreviousPeriod = Field(..., description="Сравнение с предыдущим периодом")
    expense: CategoryReport = Field(..., description="Отчет по расходам")
    income: CategoryReport = Field(..., description="Отчет по доходам")


CategoryNode.model_rebuild()
