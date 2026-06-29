from collections.abc import AsyncGenerator

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import async_session_maker
from src.core.security import oauth2_scheme
from src.repositories.accounts import AccountRepository
from src.repositories.analytics import AnalyticRepository
from src.repositories.categories import CategoryRepository
from src.repositories.transactions import TransactionRepository
from src.repositories.users import UserRepository
from src.schemas.users import User
from src.services.accounts import AccountService
from src.services.analytics import AnalyticService
from src.services.auth import AuthService
from src.services.categories import CategoryService
from src.services.transactions import TransactionService
from src.services.users import UserService


async def get_async_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


def get_user_repository(db: AsyncSession = Depends(get_async_db)) -> UserRepository:
    return UserRepository(db=db)


def get_category_repository(db: AsyncSession = Depends(get_async_db)) -> CategoryRepository:
    return CategoryRepository(db=db)


def get_account_repository(db: AsyncSession = Depends(get_async_db)) -> AccountRepository:
    return AccountRepository(db=db)


def get_transaction_repository(db: AsyncSession = Depends(get_async_db)) -> TransactionRepository:
    return TransactionRepository(db=db)


def get_analytic_repository(db: AsyncSession = Depends(get_async_db)) -> AnalyticRepository:
    return AnalyticRepository(db=db)


def get_user_service(repo: UserRepository = Depends(get_user_repository)) -> UserService:
    return UserService(user_repo=repo)


def get_auth_service(user_repo: UserRepository = Depends(get_user_repository)) -> AuthService:
    return AuthService(user_repo=user_repo)


def get_category_service(repo: CategoryRepository = Depends(get_category_repository)) -> CategoryService:
    return CategoryService(category_repo=repo)


def get_account_service(
        account_repo: AccountRepository = Depends(get_account_repository),
        transaction_repo: TransactionRepository = Depends(get_transaction_repository),
) -> AccountService:
    return AccountService(
        account_repo=account_repo,
        transaction_repo=transaction_repo,
    )


def get_transaction_service(
        transaction_repo: TransactionRepository = Depends(get_transaction_repository),
        account_repo: AccountRepository = Depends(get_account_repository),
        category_repo: CategoryRepository = Depends(get_category_repository),
) -> TransactionService:
    return TransactionService(
        transaction_repo=transaction_repo,
        account_repo=account_repo,
        category_repo=category_repo,
    )


def get_analytic_service(
        analytic_repo: AnalyticRepository = Depends(get_analytic_repository),
) -> AnalyticService:
    return AnalyticService(
        analytic_repo=analytic_repo,
    )


async def get_current_user(
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Получение текущего пользователя по токену."""
    return await auth_service.get_current_user(token)


async def get_current_admin(
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service),
) -> User:
    """Получение текущего админа по токену."""
    return await auth_service.get_current_admin(token)


async def get_current_member(
        token: str = Depends(oauth2_scheme),
        auth_service: AuthService = Depends(get_auth_service),
) -> User:
    return await auth_service.get_current_member(token)
