from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from loguru import logger
from slowapi.errors import RateLimitExceeded
from slowapi.extension import _rate_limit_exceeded_handler

from src.core.config import settings
from src.core.database import create_db_and_tables
from src.infrastructure.infra_logging import log_requests_middleware
from src.infrastructure.infra_rate_limiter import limiter
from src.infrastructure.security_headers import SecurityHeadersMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info({"event": "Connecting to database..."})
    try:
        await create_db_and_tables()
        logger.info({"event": "Database connected successfully"})
    except Exception as e:
        logger.error({"event": "Database connection failed", "error": str(e)})
        raise
    yield
    logger.info({"event": "Disconnecting from database..."})


def create_app() -> FastAPI:
    """Создает экземпляр FastAPI с настройками приложения."""
    app = FastAPI(
        title="PocketKeeper API",
        description="API для PocketKeeper",
        version="1.0.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
        openapi_url="/openapi.json" if settings.debug else None,
    )
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.allow_origins,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
        allow_credentials=settings.cors.allow_credentials,
    )
    # Заголовки безопастности
    app.add_middleware(SecurityHeadersMiddleware)

    # TODO: Включить на продакшене когда будет HTTPS
    app.add_middleware(GZipMiddleware)
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

    @app.middleware("http")
    async def log_requests(request: Request, call_next):
        """Логирование запросов."""
        return await log_requests_middleware(request, call_next)

    return app
