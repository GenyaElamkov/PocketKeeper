from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import BOOLEAN, DECIMAL, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import IntBase
from src.models.common import TimeBase as TimeBaseMixin


class Account(IntBase, TimeBaseMixin):
    __tablename__ = "accounts"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    account_type: Mapped[str] = mapped_column(String(20), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    initial_balance: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), default=Decimal("0.0"), nullable=False)
    balance: Mapped[Optional[Decimal]] = mapped_column(DECIMAL(10, 2), default=None, nullable=True)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True)

    transactions = relationship("Transaction", back_populates="account")
