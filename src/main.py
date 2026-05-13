from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.api.v1 import main_router
from src.core.config import settings
from src.core.database import create_db_and_tables


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Приложение запускается. Создаем базу данных...")
    await create_db_and_tables()
    print("База данных инициализирована.")
    yield
    print("Приложение завершает работу.")


app = FastAPI(
    description="API для PocketKeeper",
    lifespan=lifespan,
)


@app.get("/", name="Главная страница", tags=["Главная"])
async def root():
    """Главная страница. Список версий API."""
    return {
        "versions": {
            "v1": {"docs": "/docs"},
        },
    }


app.include_router(main_router, prefix=settings.api.prefix)
