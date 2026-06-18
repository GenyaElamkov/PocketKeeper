from datetime import date
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TransactionType(str, Enum):
    """Тип транзакции"""
    expense = "расходы"
    income = "доходы"


class TransactionCreate(BaseModel):
    """Модель для создания транзакций"""
    account_id: int = Field(..., description="Идентификатор счета, с которого списали/зачислили")
    category_id: int = Field(..., description="Категория транзакции")
    amount: Decimal = Field(
        ...,
        description="Сумма транзакции (больше 0)",
        max_digits=10,
        decimal_places=2,
        gt=0,
    )
    transaction_type: TransactionType = Field(..., description="Тип транзакции (доходы/расходы)")    # noqa
    description: str | None = Field(
        None,
        description="Комментарий/описание покупки",
        max_length=200,
    )
    transaction_date: date = Field(..., description="Дата операции (может отличаться от created_at)")


class Transaction(TransactionCreate):
    """Модель для представления транзакции"""
    id: int = Field(description="Уникальный идентификатор операции") # noqa

    model_config = ConfigDict(from_attributes=True)


class TransactionUpdate(BaseModel):
    """Модель для обновления транзакции"""
    account_id: int | None = Field(None, description="Идентификатор счета, с которого списали/зачислили")
    category_id: int | None = Field(None, description="Категория транзакции")
    amount: Decimal | None = Field(
        None,
        description="Сумма транзакции (больше 0)",
        max_digits=10,
        decimal_places=2,
        gt=0,
    )
    transaction_type: TransactionType | None = Field(None, description="Тип транзакции (доходы/расходы)")    # noqa
    description: str | None = Field(
        None,
        description="Комментарий/описание покупки",
        max_length=200,
    )
    transaction_date: date | None = Field(None, description="Дата операции (может отличаться от created_at)")


class TransactionList(BaseModel):
    """Модель для списка пагинации для транзакции"""
    items: list[Transaction] = Field(..., description="Список транзакций")
    total: int = Field(ge=0, description="Общее количество транзакций")
    page: int = Field(ge=1, description="Номер страницы")
    page_size: int = Field(ge=1, description="Количество элементов на странице")

    model_config = ConfigDict(from_attributes=True)


class TransactionRequest(BaseModel):
    """Модель для фильтрации транзакций"""
    page: int = Field(ge=1, default=1, description="Номер страницы")
    page_size: int = Field(ge=1, le=100, default=20, description="Количество элементов на странице")
    transaction_date: date | None = Field(None, description="Дата создания транзакции")
    category_id: int | None = Field(None, description="Идентификатор категории транзакции")
    account_id: int | None = Field(None, description="Идентификатор счета транзакции")
    date_sort: bool = Field(False, description="Направление сортировки по дате (asc или desc)")
