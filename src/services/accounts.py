from collections.abc import Sequence

from fastapi import HTTPException, status
from loguru import logger

from src.repositories.accounts import AccountRepository
from src.repositories.transactions import TransactionRepository
from src.schemas.accounts import Account, AccountCreate, AccountUpdate


class AccountService:
    """Сервис для работы с счетами."""
    def __init__(
            self,
            account_repo: AccountRepository,
            transaction_repo: TransactionRepository,

    ):
        self.account_repo = account_repo
        self.transaction_repo = transaction_repo

    async def get_accounts_by_user(self, user_id: int) -> Sequence[Account]:
        """Получить все счета конкретного пользователя."""
        return await self.account_repo.get_all_by_user_id(user_id)

    async def create_account(self, account: AccountCreate, user_id: int) -> Account:
        """Создать счет."""
        logger.info({"event": "account_creation_attempt", "username": user_id})

        name_account = await self.account_repo.user_account_by_name_exists(
            name=account["name"],
            user_id=user_id,
        )
        if name_account:
            logger.warning(
                {"event": "account_creation_failed", "username": user_id, "reason": "already exists"})
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Account with this name already exists",
            )
        account['balance'] = account["initial_balance"]
        new_account = await self.account_repo.create(account, user_id=user_id)

        logger.info({"event": "account_creation_success", "username": user_id})
        return new_account

    async def update_account(self, account_id: int, account: AccountUpdate, user_id: int) -> Account:
        """Обновить счет."""
        logger.info({"event": "account_updation_attempt", "username": user_id})

        db_account = await self.account_repo.get_by_id(account_id)
        if not db_account:
            logger.warning(
                {"event": "account_updation_failed", "username": user_id, "reason": "account not found"})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )

        if db_account.user_id != user_id:
            logger.warning(
                {"event": "account_updation_failed", "username": user_id, "reason": "permission denied"})
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't update an account for another user",
            )
        # Проверяем, что баланс не изменился и нет транзакций по этому счету
        if 'initial_balance' in account and account['initial_balance'] != db_account.initial_balance:
            transactions = await self.transaction_repo.transaction_exists(account_id)
            if transactions:
                logger.warning(
                    {"event": "account_updation_failed", "username": user_id, "reason": "account with transactions"})
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You can't update an account with transactions",
                )
            account['balance'] = account["initial_balance"]
        updated_account = await self.account_repo.update(account_id, account)

        logger.info({"event": "account_creation_success", "username": user_id})
        return updated_account

    async def delete_account(self, account_id: int, user_id: int) -> Account:
        """Удалить счет."""
        logger.info({"event": "account_deltion_attempt", "username": user_id, "account": account_id})

        db_account = await self.account_repo.get_by_id(account_id)
        if not db_account:
            logger.warning(
                {"event": "account_deletion_failed", "username": user_id, "reason": "account not found"})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )
        if db_account.user_id != user_id:
            logger.warning(
                {"event": "account_deletion_failed", "username": user_id, "reason": "permission denied"})
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't delete an account for another user",
            )
        deleted_account = await self.account_repo.delete(db_account)

        logger.info({"event": "account_deltion_success", "username": user_id, "reason": account_id})
        return deleted_account
