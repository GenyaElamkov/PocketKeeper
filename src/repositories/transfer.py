from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.transfers import Transfer


class TransferRepository:
    """Репозиторий для работы с переводами между своими счетами."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, transfer_id: int) -> Transfer | None:
        """Получить информацию о активном переводе по его ID."""
        filters = [
            Transfer.id == transfer_id,
            Transfer.is_active.is_(True),
        ]
        return await self.db.scalar(select(Transfer).filter(*filters))

    async def get_active_all_by_user_id(self, user_id: UUID) -> list[Transfer]:
        """Получение всех переводов между счетами пользователя."""
        filters = [
            Transfer.user_id == user_id,
            Transfer.is_active.is_(True),
        ]
        db_transfers = await self.db.scalars(select(Transfer).filter(*filters))
        return db_transfers.all()

    async def create(
            self,
            transfer_data: dict,
            user_id: UUID,
    ) -> Transfer:
        """Создать новый перевода на основе данных из запроса."""
        db_transfer = Transfer(**transfer_data, user_id=user_id)
        self.db.add(db_transfer)
        await self.db.commit()
        await self.db.refresh(db_transfer)
        return db_transfer

    async def delete(self, transfer: Transfer) -> None:
        """
        Удаляет переводы, которые были созданы до указанной даты.
        Удаление происходит мягко, то есть запись не удаляется из базы данных,
        а помечается как неактивная.
        """
        transfer.is_active = False
        await self.db.commit()
