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
    """Модель для представления переводов между своими счетами."""
    id: int = Field(description="Уникальный идентификатор операции") # noqa

    model_config = ConfigDict(from_attributes=True)


class TransferList(BaseModel):
    """Модель для представления списка переводов между своими счетами с пагинацией."""
    items: list[Transfer] = Field(..., description="Список переводов")
    total: int = Field(ge=0, description="Общее количество переводов")
    page: int = Field(ge=1, description="Номер страницы")
    page_size: int = Field(ge=1, description="Количество элементов на странице")

    model_config = ConfigDict(from_attributes=True)


class TransferRequest(BaseModel):
    """Модель для фильтрации переводов."""
    page: int = Field(ge=1, default=1, description="Номер страницы")
    page_size: int = Field(ge=1, le=100, default=20, description="Количество элементов на странице")
