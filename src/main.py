import uvicorn
from fastapi import FastAPI

from src.api import main_router

app = FastAPI(
    title="API Учет бюджета",
    description="API для PocketKeeper",
    version="0.1.0",
)


@app.get("/", name="Главная страница", tags=["Главная"])
async def root():
    return {"message": "Добро пожаловать в API учет бюджета!"}


app.include_router(main_router)


if __name__ == "__main__":
    uvicorn.run(
        "src.main:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
    )
