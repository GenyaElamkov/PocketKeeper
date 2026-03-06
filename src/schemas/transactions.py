import uuid
from datetime import date, datetime
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TransactionType(str, Enum):
    income = "расходы"
    expense = "доходы"


class TransactionCreate(BaseModel):
    """Модель для создания транзакций"""
    user_id: uuid.UUID = Field(..., description="Идентификатор пользователя, создавшего транзакцию")
    account_id: uuid.UUID = Field(..., description="Идентификатор счета, с которого списали/зачислили")
    category_id: uuid.UUID = Field(..., description="Категория транзакции")
    amount: Decimal = Field(
        ...,
        description="Сумма транзакции (больше 0)",
        max_digits=10,
        decimal_places=2,
        gt=0,
    )
    type: TransactionType = Field(..., description="Тип транзакции (доходы/расходы)")   # noqa
    description: str | None = Field(
        None,
        description="Комментарий/описание покупки",
        max_length=200,
    )
    transaction_date: date = Field(..., description="Дата операции (может отличаться от created_at)")
    created_at: datetime = Field(..., description="Когда запись внесена в систему")


class Transaction(TransactionCreate):
    """Модель для представления транзакции"""
    id: uuid.UUID = Field(description="Уникальный идентификатор операции") # noqa

    model_config = ConfigDict(from_attributes=True)
