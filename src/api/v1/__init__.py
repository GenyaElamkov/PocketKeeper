from fastapi import APIRouter

from src.api.v1.accounts import router as accounts_router
from src.api.v1.analytics import router as analytics_router
from src.api.v1.auth import router as auth_router
from src.api.v1.categories import router as categories_router
from src.api.v1.health import router as health_router
from src.api.v1.transactions import router as transactions_router
from src.api.v1.transfers import router as transfers_router
from src.api.v1.users import router as users_router

main_router = APIRouter()

main_router.include_router(health_router)
main_router.include_router(users_router)
main_router.include_router(auth_router)
main_router.include_router(accounts_router)
main_router.include_router(categories_router)
main_router.include_router(transactions_router)
main_router.include_router(transfers_router)
main_router.include_router(analytics_router)
