import uuid

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker

DATABASE_URL = "sqlite:///poketkeeper.db"

engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine)


class Base(DeclarativeBase):
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True) # noqa
