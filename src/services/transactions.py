from src.repositories.transactions import TransactionRepository
from src.schemas.transactions import TransactionList, TransactionRequest


class TransactionService:
    """Сервис для работы с транзакциями."""
    def __init__(self, transaction_repo: TransactionRepository):
        self.transaction_repo = transaction_repo

    async def get_all(self, request: TransactionRequest, user_id: int) -> TransactionList:
        """Получить все транзакции конкретного пользователя."""
        items, total = await self.transaction_repo.get_filtered(
            user_id=user_id,
            page=request.page,
            page_size=request.page_size,
            transaction_date=request.transaction_date,
            category_id=request.category_id,
            account_id=request.account_id,
        )

        return {
            "items": items,
            "total": total,
            "page": request.page,
            "page_size": request.page_size,
        }
