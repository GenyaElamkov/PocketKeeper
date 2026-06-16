from decimal import Decimal
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, model_validator


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
    account_type: AccountType = Field(..., description="Тип счета (cash, card, deposit)") # noqa
    currency: AccountCurrency = Field(..., description="Код валюты (RUB, USD)")
    initial_balance: Decimal = Field(
        ...,
        description="Начальный баланс",
        max_digits=10,
        decimal_places=2,
    )

    @model_validator(mode="before")
    @classmethod
    def strip_name(cls, values):
        if isinstance(values, dict):
            if "name" in values:
                values["name"] = values["name"].strip()
        return values

    @model_validator(mode="after")
    def initial_balance_must_be_non_negative(self):
        if self.initial_balance < 0:
            raise ValueError("Initial balance must be non-negative")
        return self


class Account(BaseModel):
    """Модель счета"""
    id: int = Field(..., description="Уникальный идентификатор счета пользователя")   # noqa
    name: str = Field(
        ...,
        description="Название счета (например, 'Кошелек')",
        max_length=100,
    )
    account_type: AccountType = Field(..., description="Тип счета (cash, card, deposit)") # noqa
    currency: AccountCurrency = Field(..., description="Код валюты (RUB, USD)")
    balance: Decimal | None = Field(None, description="Текущий баланс (None, если не рассчитан)",
                                    max_digits=10, decimal_places=2)
    initial_balance: Decimal = Field(
        ...,
        description="Начальный баланс",
        max_digits=10,
        decimal_places=2,
    )
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
    account_type: AccountType | None = Field(..., description="Тип счета (cash, card, deposit)") # noqa
    currency: AccountCurrency | None = Field(..., description="Код валюты (RUB, USD)")
    initial_balance: Decimal | None = Field(
        None,
        description="Начальный баланс",
        max_digits=10,
        decimal_places=2,
    )

    @model_validator(mode="before")
    @classmethod
    def strip_name(cls, values):
        if isinstance(values, dict):
            if "name" in values:
                values["name"] = values["name"].strip()
        return values

    @model_validator(mode="after")
    def intitial_balance_must_be_non_negative(self):
        if self.initial_balance is not None and self.initial_balance < 0:
            raise ValueError("Initial balance must be non-negative")
        return self
