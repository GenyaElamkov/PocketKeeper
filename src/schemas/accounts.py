import uuid
from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class AccountCurrency(str, Enum):
    """Валюта счета"""
    RUB = "RUB"
    USD = "USD"
    EUR = "EUR"


class AccountType(str, Enum):
    """Тип счета"""
    cash = "наличные"
    card = "карта"
    savings = "экономия"
    credit = "кредит"
    deposit = "депозит"


class AccountsCreate(BaseModel):
    """Модель для создания счета пользователем"""
    name: str = Field(
        ...,
        description="Название счета (например, 'Кошелек')",
        max_length=100,
    )
    type: AccountType = Field(..., description="Тип счета (cash, card, deposit)") # noqa
    currency: AccountCurrency = Field(..., description="Код валюты (RUB, USD)")
    balance: Decimal = Field(
        ...,
        description="Текущий баланс",
        max_digits=10,
        decimal_places=2,
    )
    is_archived: bool = Field(
        default=False,
        description="Архивирован ли счет (скрыт из выбора)",
    )


class Account(AccountsCreate):
    """Модель счета"""
    id: uuid.UUID = Field(..., description="Уникальный идентификатор счета пользователя")   # noqa
    user_id: uuid.UUID = Field(..., decription="Владелец счета")

    model_config = ConfigDict(from_attributes=True)
