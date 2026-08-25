from uuid import UUID

from fastapi import HTTPException, status
from loguru import logger

from src.repositories.accounts import AccountRepository
from src.repositories.transfer import TransferRepository
from src.schemas.transfers import Transfer, TransferCreate


class TransferService:
    """Сервис для работы с переводами совешенными между своими счетами."""

    def __init__(
            self,
            transfer_repo=TransferRepository,
            account_repo=AccountRepository,
    ):
        self.transfer_repo = transfer_repo
        self.account_repo = account_repo

    async def create_transfer(self, transfer: TransferCreate, user_id: UUID) -> Transfer:
        """Создать перевод между своими счетами."""
        logger.info({"event": "transfer_creation_attempt", "user_id": user_id})

        # Проверка наличия счета.
        to_account = await self.account_repo.get_by_id(account_id=transfer.to_account_id)
        from_account = await self.account_repo.get_by_id(account_id=transfer.from_account_id)
        if (to_account and from_account) is None:
            logger.warning({"event": "transfer_creation_failed", "user_id": user_id, "reason": "account not found"})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )

        # Проверка на user, принадлежит user счет.
        if to_account.user_id != user_id or from_account.user_id != user_id:
            logger.warning(
                {"event": "transfer_creation_failed", "user_id": user_id, "reason": "can't create for another user"})
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="The user is attempting to transfer funds to or from someone else's account.",
            )

        # Проверка на возможность перевода себе.
        if to_account == from_account:
            logger.warning(
                {"event": "transfer_creation_failed", "user_id": user_id, "reason": "between the same accounts"})
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot send money between the same accounts.",
            )

        # Провекра на отрицательные баланс. Достаточно баланса для перевода
        if from_account.balance < transfer.amount:
            logger.warning(
                {"event": "transfer_creation_failed", "user_id": user_id, "reason": "insufficient funds"})
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Insufficient funds",
            )

        # Проверка на cовпадение валют. Конвертация не поддерживаеится.
        if to_account.currency != from_account.currency:
            logger.warning(
                {"event": "transfer_creation_failed", "user_id": user_id, "reason": "currency mismatch"})
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Currency mismatch",
            )

        from_account.balance -= transfer.amount
        to_account.balance += transfer.amount
        new_transfer = await self.transfer_repo.create(
            transfer.model_dump(exclude_unset=True),
            user_id,
        )
        logger.info({"event": "transfer_creation_success", "user_id": user_id})
        return new_transfer

    async def delete_transfer(self, transfer_id: int, user_id: UUID) -> Transfer:
        """Удалить перевод совершенный между своими счетами."""
        logger.info({"event": "transfer_deletion_attempt", "user_id": user_id})

        db_transfer = await self.transfer_repo.get_by_id(transfer_id)
        if db_transfer is None:
            logger.warning(
                {"event": "transfer_deletion_failed", "user_id": user_id, "reason": "transfer not found"})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Transfer not found",
            )

        if db_transfer.user_id != user_id:
            logger.warning({"event": "transfer_deletion_failed", "user_id": user_id, "reason": "permission denied"})
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You can't delete a transfer for another user",
            )

        to_account = await self.account_repo.get_by_id(account_id=db_transfer.to_account_id)
        from_account = await self.account_repo.get_by_id(account_id=db_transfer.from_account_id)
        if (to_account and from_account) is None:
            logger.warning({"event": "transfer_creation_failed", "user_id": user_id, "reason": "account not found"})
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Account not found",
            )

        to_account.balance -= db_transfer.amount
        from_account.balance += db_transfer.amount
        logger.info({"event": "account_balance_updated", "user_id": user_id})

        await self.transfer_repo.delete(db_transfer)
        logger.info({"event": "transfer_deletion_success", "user_id": user_id})

        return db_transfer
