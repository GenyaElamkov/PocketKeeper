from fastapi import HTTPException, status
from loguru import logger

from src.repositories.accounts import AccountRepository
from src.repositories.categories import CategoryRepository
from src.repositories.transactions import TransactionRepository
from src.schemas.transactions import (Transaction, TransactionCreate,
                                      TransactionList, TransactionRequest,
                                      TransactionUpdate)


class TransactionService:
    """Сервис для работы с транзакциями."""
    def __init__(
            self,
            transaction_repo: TransactionRepository,
            account_repo: AccountRepository,
            category_repo: CategoryRepository,
    ):
        self.transaction_repo = transaction_repo
        self.account_repo = account_repo
        self.category_repo = category_repo

    async def get_all(self, request: TransactionRequest, user_id: int) -> TransactionList:
        """Получить все транзакции конкретного пользователя."""
        items, total = await self.transaction_repo.get_filtered(
            user_id=user_id,
            page=request.page,
            page_size=request.page_size,
            transaction_date=request.transaction_date,
            date_from=request.date_from,
            date_to=request.date_to,
            category_id=request.category_id,
            account_id=request.account_id,
            transaction_type=request.transaction_type,
            date_sort=request.date_sort,
        )
        return {
            "items": items,
            "total": total,
            "page": request.page,
            "page_size": request.page_size,
        }

    async def create_transaction(self, transaction: TransactionCreate, user_id: int) -> Transaction:
        """Создать транзакцию."""
        logger.info({"event": "transaction_creation_attempt", "username": user_id})

        account = await self.account_repo.get_by_id(transaction.account_id)
        if account is None:
            logger.warning({"event": "transaction_creation_failed", "username": user_id, "reason": "account not found"})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )
        category = await self.category_repo.get_by_id(category_id=transaction.category_id)
        if category is None:
            logger.warning(
                {"event": "transaction_creation_failed", "username": user_id, "reason": "category not found"})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found",
            )
        new_transaction = await self.transaction_repo.create(
            transaction.model_dump(exclude_unset=True),
            user_id=user_id,
        )
        await self.transaction_repo.update_account_balance(transaction.account_id)

        logger.info({"event": "transaction_creation_success", "username": user_id})
        return new_transaction

    async def update_transaction(
            self,
            transaction_id: int,
            update_data: TransactionUpdate,
            user_id: int,
    ) -> Transaction:
        """Обновить транзакцию."""
        logger.info({"event": "transaction_update_attempt", "username": user_id})

        db_transaction = await self.transaction_repo.get_active_transaction_by_id(transaction_id)
        if db_transaction is None:
            logger.warning(
                {"event": "transaction_update_failed", "username": user_id, "reason": "transaction not found"})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found",
            )
        if db_transaction.user_id != user_id:
            logger.warning({"event": "transaction_update_failed", "username": user_id, "reason": "permission denied"})
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't update a transaction for another user",
            )
        await self.transaction_repo.update(transaction_id, update_data.model_dump(exclude_unset=True))
        logger.info({"event": "transaction_update_success", "username": user_id})

        await self.transaction_repo.update_account_balance(update_data.account_id)
        logger.info({"event": "account_balance_updated", "username": user_id})

        return await self.transaction_repo.get_active_transaction_by_id(transaction_id)

    async def delete_transaction(self, transaction_id: int, user_id: int) -> Transaction:
        """Удалить транзакцию."""
        logger.info({"event": "transaction_deletion_attempt", "username": user_id})

        db_transaction = await self.transaction_repo.get_active_transaction_by_id(transaction_id)
        if db_transaction is None:
            logger.warning(
                {"event": "transaction_deletion_failed", "username": user_id, "reason": "transaction not found"})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transaction not found",
            )

        if db_transaction.user_id != user_id:
            logger.warning({"event": "transaction_deletion_failed", "username": user_id, "reason": "permission denied"})
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't delete a transaction for another user",
            )
        await self.transaction_repo.delete(db_transaction)
        logger.info({"event": "transaction_deletion_success", "username": user_id})

        await self.transaction_repo.update_account_balance(db_transaction.account_id)
        logger.info({"event": "account_balance_updated", "username": user_id})

        return db_transaction
