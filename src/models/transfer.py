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
    from models.users import User


class Transfer(IntBase, TimeBaseMixin):
    """Модель для первода между своими счетасми."""
    __tablename__ = "transfers"

    __table_args__ = (
        Index("ix_transfer_user_id", "user_id"),
        Index("ix_transfer_account_id", "account_id"),
        Index("ix__transfer_date", "transfer_date"),
    )

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    from_account_id: Mapped[int] = mapped_column(ForeignKey("account.id"), nullable=False)
    to_account_id: Mapped[int] = mapped_column(ForeignKey("account.id"), nullable=False)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    description: Mapped[str | None] = mapped_column(String(200), nullable=True)
    transfer_date: Mapped[date] = mapped_column(DATE, nullable=False)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True)

    user: Mapped["User"] = relationship("User", back_populates="transfers")
    account: Mapped["Account"] = relationship("Account", back_populates="transfers")
