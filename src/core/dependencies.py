from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_maker
from src.repositories.accounts import AccountRepository
from src.repositories.categories import CategoryRepository
from src.services.accounts import AccountService
from src.services.categories import CategoryService


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


def get_category_repository(db: AsyncSession = Depends(get_async_db)) -> CategoryRepository:
    return CategoryRepository(db=db)


def get_accouht_repository(db: AsyncSession = Depends(get_async_db)) -> AccountRepository:
    return AccountRepository(db=db)


def get_category_service(repo: CategoryRepository = Depends(get_category_repository)) -> CategoryService:
    return CategoryService(category_repo=repo)


def get_account_service(repo: AccountRepository = Depends(get_accouht_repository)) -> AccountService:
    return AccountService(account_repo=repo)
