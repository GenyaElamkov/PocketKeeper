from collections.abc import Sequence

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account


class AccountRepository:
    """Репозиторий для работы с счетами."""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, account_id: int) -> Account | None:
        """Получить счет по ID."""
        db_account = await self.db.scalar(
            select(Account).filter(Account.id == account_id),
        )
        return db_account

    async def get_all_by_user_id(self, user_id: int) -> Sequence[Account]:
        """Получить счета пользователя."""
        db_acount = await self.db.scalars(
            select(Account).filter(Account.user_id == user_id),
        )
        return db_acount.all()

    async def get_user_account_by_name(self, data: dict, user_id: int) -> Account | None:
        """Получить счет пользователя по имени."""
        filters = [
            Account.name == data['name'],
            Account.user_id == user_id,
        ]
        return await self.db.scalar(select(Account).filter(*filters))

    async def create(self, data: dict, user_id: int) -> Account:
        """Создать счет."""
        db_account = Account(**data, user_id=user_id)
        self.db.add(db_account)
        await self.db.commit()
        await self.db.refresh(db_account)
        return db_account

    async def update(self, account_id: int, data: dict) -> Account | None:
        """Обновить счет."""
        await self.db.execute(
            update(Account)
            .where(Account.id == account_id)
            .values(**data),
        )
        await self.db.commit()
        return await self.get_by_id(account_id)

    async def delete(self, account_id: int) -> Account:
        """Удалить счет."""
        db_account = await self.get_by_id(account_id)
        db_account.is_active = False
        await self.db.commit()
        await self.db.refresh(db_account)
        return db_account
