from typing import TYPE_CHECKING
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.core.database import IntBase
from src.models.common import TimeBase as TimeBaseMixin

if TYPE_CHECKING:
    from models.transactions import Transaction


class Category(IntBase, TimeBaseMixin):
    __tablename__ = "categories"

    user_id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(50))
    icon: Mapped[str | None] = mapped_column(String(200), nullable=True)
    parent_id: Mapped[int | None] = mapped_column(
        ForeignKey("categories.id"),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="category", cascade="all, delete-orphan",
    )
    user = relationship("User", back_populates="categories")
    parent: Mapped["Category | None"] = relationship(
        "Category", back_populates="children", remote_side="Category.id",
    )
    children: Mapped[list["Category"]] = relationship("Category", back_populates="parent")
