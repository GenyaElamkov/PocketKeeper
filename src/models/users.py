from datetime import datetime
from sqlalchemy import String, BOOLEAN, TIMESTAMP
from sqlalchemy.orm import Mapped, mapped_column
from src.database import Base


class User(Base):
    __tablename__ = 'users'

    email: Mapped[str] = mapped_column(String(254), unique=True)
    hashed_password: Mapped[str] = mapped_column(String(254), nullable=False)
    full_name: Mapped[str] = mapped_column(String(254), nullable=False)
    is_active: Mapped[bool] = mapped_column(BOOLEAN, default=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, Mdefault=datetime.now())