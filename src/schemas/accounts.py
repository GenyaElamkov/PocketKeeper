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


class AccountCreate(BaseModel):
    """Модель для создания счета пользователем"""
    name: str = Field(
        ...,
        description="Название счета (например, 'Кошелек')",
        max_length=100,
    )
    type: AccountType = Field(..., description="Тип счета (cash, card, deposit)") # noqa
    currency: AccountCurrency = Field(..., description="Код валюты (RUB, USD)")
    initial_balance: Decimal = Field(
        ...,
        description="Текущий баланс",
        max_digits=10,
        decimal_places=2,
    )


class Account(BaseModel):
    """Модель счета"""
    id: int = Field(..., description="Уникальный идентификатор счета пользователя")   # noqa
    name: str = Field(
        ...,
        description="Название счета (например, 'Кошелек')",
        max_length=100,
    )
    type: AccountType = Field(..., description="Тип счета (cash, card, deposit)") # noqa
    currency: AccountCurrency = Field(..., description="Код валюты (RUB, USD)")
    balance: Decimal | None = Field(None, description="Текущий баланс",
                                    max_digits=10, decimal_places=2)
    is_active: bool = Field(
        default=False,
        description="Архивирован ли счет (скрыт из выбора)",
    )

    model_config = ConfigDict(from_attributes=True)


class AccountUpdate(BaseModel):
    """Модель для обновления счета"""
    name: str | None = Field(
        None,
        description="Название счета (например, 'Кошелек')",
        max_length=100,
    )
    type: AccountType | None = Field(..., description="Тип счета (cash, card, deposit)") # noqa
    currency: AccountCurrency | None = Field(..., description="Код валюты (RUB, USD)")
    initial_balance: Decimal | None = Field(
        None,
        description="Текущий баланс",
        max_digits=10,
        decimal_places=2,
    )
    is_active: bool | None = Field(None, description="Архивирован ли счет (скрыт из выбора)")
