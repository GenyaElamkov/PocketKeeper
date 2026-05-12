from fastapi import FastAPI

from src.api.v1 import main_router
from src.config import settings

app = FastAPI(description="API для PocketKeeper")


@app.get("/", name="Главная страница", tags=["Главная"])
async def root():
    """Главная страница. Список версий API."""
    return {
        "versions": {
            "v1": {"docs": "/docs"},
        },
    }


app.include_router(main_router, prefix=settings.api.prefix)
