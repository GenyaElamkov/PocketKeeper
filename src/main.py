import uvicorn
from fastapi import FastAPI
from api import (
    users,
    accounts, 
    categories, 
    transactions
)

app = FastAPI(
    title="API Учет бюджета",
    description="API для PocketKeeper",
    version="0.1.0",
)



@app.get("/", name="Главная страница", tags=["Главная"])
async def root():
    return {"message": "Добро пожаловать в API учет бюджета!"}


app.include_router(users.router)
app.include_router(accounts.router)
app.include_router(categories.router)
app.include_router(transactions.router)


if __name__ == "__main__":
    uvicorn.run(
        "main:app", 
        host="127.0.0.1", 
        port=8000,
        reload=True,
    )
    