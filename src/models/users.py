from typing import TYPE_CHECKING

from sqlalchemy import BOOLEAN, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.common import TimeBase as TimeBaseMixin

if TYPE_CHECKING:
    from models.categories import Category
    from models.transactions import Transaction


class User(Base, TimeBaseMixin):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(String(254), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(254), nullable=False)
    full_name: Mapped[str] = mapped_column(String(254), nullable=False)
    role: Mapped[str] = mapped_column(String(20), default="member", index=True)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True, index=True)

    categories: Mapped[list["Category"]] = relationship("Category", back_populates="user")
    transactions: Mapped[list["Transaction"]] = relationship("Transaction", back_populates="user")
