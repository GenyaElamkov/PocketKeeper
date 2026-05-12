from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import BOOLEAN, DATE, DECIMAL, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.common import TimeBase as TimeBaseMixin

if TYPE_CHECKING:
    from models.accounts import Account
    from models.categories import Category
    from models.users import User


class Transaction(Base, TimeBaseMixin):
    __tablename__ = "transactions"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)   # noqa
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    transaction_date: Mapped[date] = mapped_column(DATE, nullable=False)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True)

    user: Mapped["User"] = relationship("User", back_populates="transactions")
    category: Mapped["Category"] = relationship("Category", back_populates="transactions")
    account: Mapped["Account"] = relationship("Account", back_populates="transactions")
