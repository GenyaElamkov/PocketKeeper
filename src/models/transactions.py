from datetime import date
from decimal import Decimal
from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import BOOLEAN, DATE, DECIMAL, ForeignKey, Index, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import IntBase
from src.models.common import TimeBase as TimeBaseMixin

if TYPE_CHECKING:
    from models.accounts import Account
    from models.categories import Category
    from models.users import User


class Transaction(IntBase, TimeBaseMixin):
    """Модель для транзакций."""
    __tablename__ = "transactions"

    __table_args__ = (
        Index("ix_transactions_user_id", "user_id"),
        Index("ix_transactions_account_id", "account_id"),
        Index("ix_transactions_category_id", "category_id"),
        Index("ix_transactions_transaction_date", "transaction_date"),
    )

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    account_id: Mapped[int] = mapped_column(ForeignKey("accounts.id"), nullable=False)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    transaction_type: Mapped[str] = mapped_column(nullable=False)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    transaction_date: Mapped[date] = mapped_column(DATE, nullable=False)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True)

    user: Mapped["User"] = relationship("User", back_populates="transactions")
    category: Mapped["Category"] = relationship("Category", back_populates="transactions")
    account: Mapped["Account"] = relationship("Account", back_populates="transactions")
