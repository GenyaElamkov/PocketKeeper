from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from src.api.v1 import main_router
from src.core.config import settings
from src.core.database import create_db_and_tables
from src.infrastructure.infra_logging import log_requests_middleware


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

origins = [
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логирование запросов."""
    return await log_requests_middleware(request, call_next)


@app.get("/", name="Главная страница", tags=["Главная"])
async def root():
    """Главная страница. Список версий API."""
    logger.info("Запрос на главную страницу")
    return {
        "versions": {
            "v1": {"docs": "/docs"},
        },
    }


app.include_router(main_router, prefix=settings.api.prefix)
