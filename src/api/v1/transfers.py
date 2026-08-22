from fastapi import APIRouter, Depends, Request, status

from src.core.dependencies import get_current_member, get_transfer_service
from src.infrastructure.infra_rate_limiter import limiter
from src.schemas.transfers import Transfer, TransferCreate
from src.schemas.users import User
from src.services.transfer import TransferService

router = APIRouter(
    prefix="/v1",
    tags=["Переводы"],
)


@router.post(
        "/transfers",
        name="Создать перевод между своими счетами",
        response_model=Transfer,
        status_code=status.HTTP_201_CREATED,
        summary="Создать новую транзакцию (перевод) мережду своими счетами",
        description="""
        Создаёт новую перевод между своими счетами.
        Баланс счёта автоматически обновляется.
        Не учитывается в транзакциях.
        """,
        response_description="Новая созданная запись о переводе",
        )
@limiter.limit("5/minute")
async def create_transfer_between_accounts(
    request: Request,
    transfer: TransferCreate,
    transfer_service: TransferService = Depends(get_transfer_service),
    current_user: User = Depends(get_current_member),
):
    """Создание перевода между свими счетами."""
    return await transfer_service.create_transfer(transfer, current_user.id)
