from datetime import date
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TransferCreate(BaseModel):
    """Модель для создании перевода между счетамию."""
    from_account_id: int = Field(...,  description="Индификтор счета от")
    to_account_id: int = Field(..., description="Индификатор счета куда")
    amount: Decimal = Field(..., description="Сумма перевода (больше 0)", max_digits=10, decimal_places=2, gt=0)
    description: str | None = Field(None, description="Коментарий/описание перевода", max_length=200)
    transfer_date: date = Field(..., description="Дата операции (может отличаться от created_at)")


class Transfer(TransferCreate):
    id: int = Field(description="Уникальный идентификатор операции") # noqa

    model_config = ConfigDict(from_attributes=True)
