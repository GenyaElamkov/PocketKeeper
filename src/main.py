from fastapi import Request
from loguru import logger

from src.api.v1 import main_router
from src.application.app_factory import create_app
from src.core.config import settings
from src.infrastructure.infra_rate_limiter import limiter

app = create_app()


@app.get("/", name="Главная страница", tags=["Главная"])
@limiter.limit("10/minute")
async def root(request: Request):
    """Главная страница. Список версий API."""
    logger.info("Запрос на главную страницу")
    return {
        "versions": {
            "v1": {"docs": "/docs"},
        },
    }


app.include_router(main_router, prefix=settings.api.prefix)
