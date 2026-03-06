import uuid
from decimal import Decimal

from sqlalchemy import BOOLEAN, DECIMAL, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.database import Base


class Account(Base):
    __tablename__ = "accounts"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    type: Mapped[str] = mapped_column(String(20), nullable=False)   # noqa
    currency: Mapped[str] = mapped_column(String(3), nullable=False)
    balance: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    is_archived: Mapped[bool] = mapped_column(BOOLEAN, default=False)
