from fastapi import APIRouter

from src.api.accounts import router as accounts_router
from src.api.auth import router as auth_router
from src.api.categories import router as categories_router
from src.api.transactions import router as transactions_router
from src.api.users import router as users_router

main_router = APIRouter()

main_router.include_router(users_router)
main_router.include_router(auth_router)
main_router.include_router(accounts_router)
main_router.include_router(categories_router)
main_router.include_router(transactions_router)
