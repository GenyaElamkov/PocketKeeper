from uuid import UUID, uuid4

from sqlalchemy.ext.asyncio import (AsyncSession, async_sessionmaker,
                                    create_async_engine)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from src.core.config import settings

DATABASE_URL = settings.database.url

async_engine = create_async_engine(
    DATABASE_URL,
    pool_size=settings.database.pool_size,
    max_overflow=settings.database.max_overflow,
    pool_timeout=settings.database.pool_timeout,
    pool_recycle=settings.database.pool_recycle,
    pool_pre_ping=settings.database.pool_pre_ping,
    echo=settings.database.echo,
)

async_session_maker = async_sessionmaker(
    async_engine,
    expire_on_commit=False,
    class_=AsyncSession,
)


class Base(DeclarativeBase):
    pass


class UUIDBase(Base):
    """Базовый класс с UUID для защищенных сущностей"""
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(   # noqa
        primary_key=True,
        default=uuid4,
        server_default="gen_random_uuid()",
    )


class IntBase(Base):
    """Базовый класс с Integer ID для внутренних сущностей"""
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, index=True) # noqa


async def create_db_and_tables():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
