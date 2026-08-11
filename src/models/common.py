from datetime import datetime, timezone

from sqlalchemy import DateTime, func
from sqlalchemy.orm import Mapped, mapped_column


def get_current_dt() -> datetime:
    """Получить текущую дату и время"""
    return datetime.now(tz=timezone.utc)


class TimeBase:
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_current_dt,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_current_dt,
        onupdate=func.now(),
        nullable=False,
    )
