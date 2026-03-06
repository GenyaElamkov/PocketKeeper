import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base

if TYPE_CHECKING:
    from src.models.transactions import Transaction


class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(50), unique=True)
    icon: Mapped[str | None] = mapped_column(String(200), nullable=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(ForeignKey("categories.id"), nullable=True)
    transactions: Mapped[list["Transaction"]] = relationship(
        "Transaction", back_populates="category", cascade="all, delete-orphan",
    )

    parrent: Mapped["Category | None"] = relationship("Category", back_populates="children", remote_side="Category.id")
    children: Mapped[list["Category"]] = relationship("Category", back_populates="parrent")
