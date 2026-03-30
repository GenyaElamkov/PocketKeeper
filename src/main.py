from fastapi import FastAPI
from fastapi.responses import JSONResponse

from src.api import main_router

app = FastAPI(
    title="API Учет бюджета",
    description="API для PocketKeeper",
    version="0.1.0",
)


@app.get("/", name="Главная страница", tags=["Главная"])
async def root():
    content = {"message": "Добро пожаловать в API учет бюджета!"}
    return JSONResponse(content=content, media_type="application/json; charset=utf-8")

app.include_router(main_router)
