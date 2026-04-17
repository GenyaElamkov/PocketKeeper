from fastapi import FastAPI

from src.api.v1 import main_router

app = FastAPI(description="API для PocketKeeper")


@app.get("/", name="Главная страница", tags=["Главная"])
async def root():
    """Главная страница. Список версий API."""
    return {
        "versions": {
            "v1": {"docs": "/docs"},
        },
    }


app.include_router(main_router, prefix="/v1")
