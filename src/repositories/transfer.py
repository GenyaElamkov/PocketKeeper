from sqlalchemy.ext.asyncio import AsyncSession


class TransferRepository:
    """Репозиторий для работы с переводами между своими счетами."""

    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self) -> None:
        """Создать новый перевода на основе данных из запроса."""

    async def get_by_id(self) -> None:
        """Получить информацию о конкретном платеже по его ID."""

    async def get_all_by_user_id(self) -> None:
        """ Получение всех переводов пользователя."""

    async def delete(self) -> None:
        """Удаляет переводы, которые были созданы до указанной даты."""
