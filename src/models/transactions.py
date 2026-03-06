import uuid
from datetime import datetime
from decimal import Decimal
from typing import TYPE_CHECKING

from sqlalchemy import DATE, DECIMAL, TIMESTAMP, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.accounts import Account
    from src.models.categories import Category
    from src.models.users import User


class Transaction(Base):
    __tablename__ = "transactions"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    account_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    category_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("categories.id"), nullable=False)
    ammount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    type: Mapped[str] = mapped_column(nullable=False)   # noqa
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    date: Mapped[date] = mapped_column(DATE, nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, nullable=False)

    user: Mapped["User"] = relationship("User", back_populates="transactions")
    category: Mapped["Category"] = relationship("Category", back_populates="transactions")
    account: Mapped["Account"] = relationship("Account", back_populates="transactions")
