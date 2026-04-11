from typing import TYPE_CHECKING

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base
from src.models.common import TimeBase as TimeBaseMixin

if TYPE_CHECKING:
    from src.models.transactions import Transaction


class Category(Base, TimeBaseMixin):
    __tablename__ = "categories"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(50))
    icon: Mapped[str | None] = mapped_column(String(200), nullable=True)
    parent_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="category", cascade="all, delete-orphan",
    )
    user = relationship("User", back_populates="categories")
    parent: Mapped["Category | None"] = relationship(
        "Category", back_populates="children", remote_side="Category.id",
    )
    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent")
