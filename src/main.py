from fastapi import FastAPI

from src.api.v1 import main_router
from src.versioning import create_versions_app

app = FastAPI(description="API для PocketKeeper")

app_v1 = create_versions_app("0.1.0", "API Учет бюджета v1")


@app.get("/", name="Главная страница", tags=["Главная"])
async def root():
    """Главная страница. Список версий API."""
    return {
        "versions": {
            "v1": {"docs": "v1/docs"},
        },
    }


app_v1.include_router(main_router)

app.mount("/v1", app_v1)
