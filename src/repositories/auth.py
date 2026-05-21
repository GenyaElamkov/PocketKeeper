from sqlalchemy.ext.asyncio import AsyncSession


class AuthRepository:
    """Репозиторий для работы с пользователями."""
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_login(self, user_id: int, ip_address: str, user_agent: str) -> None:
        """Создать логин пользователя."""
