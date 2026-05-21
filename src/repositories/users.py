from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.users import User


class UserRepository:
    """Репозиторий для работы с пользователями."""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, user_id: int) -> User | None:
        """Получить пользователя по ID."""
        return await self.db.scalar(select(User).filter(User.id == user_id))

    async def get_active_by_id(self, user_id: int) -> User | None:
        """Получить активного пользователя по ID."""
        filters = [
            User.id == user_id,
            User.is_active.is_(True),
        ]
        return await self.db.scalar(select(User).filter(*filters))

    async def get_all(self, page: int, page_size: int) -> tuple[User, int]:
        """Получить всех пользователей по ID."""
        total_stmt = select(func.count()).select_from(User)
        total = await self.db.scalar(total_stmt) or 0
        users_stmt = (
            select(User)
            .order_by(
                User.is_active.is_(True).desc(),
                User.email,
            )
            .offset((page - 1) * page_size)
            .limit(page_size)
        )
        items = (await self.db.scalars(users_stmt)).all()
        return items, total

    async def create(self, email: str, hashed_password: str, full_name: str) -> User:
        """Создать пользователя."""
        db_user = User(
            email=email,
            hashed_password=hashed_password,
            full_name=full_name,
        )
        self.db.add(db_user)
        await self.db.commit()
        return db_user

    async def update(
            self,
            user_id: int,
            email: str | None,
            password: str | None,
            full_name: str | None,
    ) -> User:
        """Обновить пользователя."""
        await self.db.execute(
            update(User)
            .where(User.id == user_id)
            .values(
                email=email,
                hashed_password=password,
                full_name=full_name,
            ),
        )
        await self.db.commit()
        return await self.get_by_id(user_id)

    async def delete(self, user_delete: User) -> User:
        """Удалить пользователя."""
        user_delete.is_active = False
        await self.db.commit()
        await self.db.refresh(user_delete)
        return user_delete

    async def user_exists(self, email: str) -> bool:
        """Проверить, существует ли пользователь с таким email."""
        return await self.db.scalar(select(User).where(User.email == email)) is not None
