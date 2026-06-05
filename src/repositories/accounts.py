from collections.abc import Sequence

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account


class AccountRepository:
    """Репозиторий для работы с счетами."""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, account_id: int) -> Account | None:
        """Получить активный счет по ID."""
        filters = [
            Account.id == account_id,
            Account.is_active.is_(True),
        ]
        return await self.db.scalar(select(Account).filter(*filters))

    async def get_all_by_user_id(self, user_id: int) -> Sequence[Account]:
        """Получить счета пользователя."""
        filters = [
            Account.user_id == user_id,
            Account.is_active.is_(True),
        ]
        db_acount = await self.db.scalars(
            select(Account).filter(*filters),
        )
        return db_acount.all()

    async def user_account_by_name_exists(self, name: str, user_id: int) -> bool:
        """Проверить, что счет пользователя с таким именем уже существует."""
        filters = [
            func.lower(Account.name) == name.lower(),
            Account.user_id == user_id,
            Account.is_active.is_(True),
        ]
        return await self.db.scalar(select(Account).filter(*filters)) is not None

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

    async def delete(self, delete_account: Account) -> Account:
        """Удалить счет."""
        delete_account.is_active = False
        await self.db.commit()
        await self.db.refresh(delete_account)
        return delete_account
