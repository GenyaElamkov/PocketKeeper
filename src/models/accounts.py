from decimal import Decimal

from sqlalchemy import BOOLEAN, DECIMAL, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.common import TimeBase


class Account(Base, TimeBase):
    __tablename__ = "accounts"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)   # noqa
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    balance: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    is_archived: Mapped[bool] = mapped_column(BOOLEAN, default=False)

    transactions = relationship("Transaction", back_populates="account")
