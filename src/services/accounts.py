from collections.abc import Sequence

from fastapi import HTTPException, status

from src.repositories.accounts import AccountRepository
from src.schemas.accounts import Account, AccountCreate, AccountUpdate


class AccountService:
    """Сервис для работы с счетами."""
    def __init__(self, account_repo: AccountRepository):
        self.account_repo = account_repo

    async def get_accounts_by_user(self, user_id: int) -> Sequence[Account]:
        """Получить все счета конкретного пользователя."""
        db_accounts = await self.account_repo.get_all_by_user_id(user_id)
        if not db_accounts:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Accounts not found",
            )
        return db_accounts

    async def create_account(self, account: AccountCreate, user_id: int) -> Account:
        """Создать аккаунт."""
        # Проверяем, что счет с таким именем уже существует
        name_account = await self.account_repo.user_account_by_name_exists(
            name=account["name"],
            user_id=user_id,
        )
        if name_account:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Account with this name already exists",
            )
        return await self.account_repo.create(account, user_id=user_id)

    async def update_account(self, account_id: int, account: AccountUpdate, user_id: int) -> Account:
        """Обновить счет."""
        db_account = await self.account_repo.get_by_id(account_id)
        if not db_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )

        if db_account.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't update an account for another user",
            )
        return await self.account_repo.update(account_id, account.model_dump())

    async def delete_account(self, account_id: int, user_id: int) -> Account:
        """Удалить счет."""
        db_account = await self.account_repo.get_by_id(account_id)
        if not db_account:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )
        if db_account.user_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't delete an account for another user",
            )
        return await self.account_repo.delete(db_account)
