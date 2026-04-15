from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.db_depends import get_async_db
from src.auth import get_current_member
from src.balance import update_account_balance
from src.models.accounts import Account as AccountModel
from src.models.categories import Category as CategoryModel
from src.models.transactions import Transaction as TransactionModel
from src.models.users import User as UserModel
from src.schemas.transactions import Transaction as TransactionSchema
from src.schemas.transactions import \
    TransactionCreate as TransactionCreateSchema
from src.schemas.transactions import TransactionList as TransactionListSchema
from src.schemas.transactions import \
    TransactionRequest as TransactionRequestSchema
from src.schemas.transactions import \
    TransactionUpdate as TransactionUpdateSchema

router = APIRouter(
    prefix="/transactions",
    tags=["Транзакции"],
)


@router.post("/", name="Создать транзакцию",
             response_model=TransactionSchema,
             status_code=status.HTTP_201_CREATED)
async def create_transaction(transaction: TransactionCreateSchema,
                             db: AsyncSession = Depends(get_async_db),
                             current_user: UserModel = Depends(get_current_member),
                             ) -> TransactionSchema:
    """Создание транзакции"""
    account = await db.scalars(
        select(AccountModel).where(
            AccountModel.id == transaction.account_id,
            AccountModel.is_active.is_(True),
        ),
    )
    if account.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Счет не найден",
        )

    category = await db.scalars(
        select(CategoryModel).where(
            CategoryModel.id == transaction.category_id,
            CategoryModel.is_active.is_(True),
        ),
    )
    if category.first() is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Категория не найдена",
        )
    db_transaction = TransactionModel(**transaction.model_dump(), user_id=current_user.id)
    db.add(db_transaction)
    await update_account_balance(db, transaction.account_id)
    await db.refresh(db_transaction)
    return db_transaction


@router.get("/", name="Список транзакций", response_model=TransactionListSchema)
async def get_all_transactions(request: TransactionRequestSchema = Depends(),
                               db: AsyncSession = Depends(get_async_db),
                               current_user: UserModel = Depends(get_current_member),
                               ) -> TransactionListSchema:
    """Список транзакций"""
    filters = [
        TransactionModel.user_id == current_user.id,
        TransactionModel.is_active.is_(True),
    ]
    if request.transaction_date is not None:
        filters.append(TransactionModel.transaction_date == request.transaction_date)

    total_stmt = select(func.count()).select_from(TransactionModel).where(*filters)
    total = await db.scalar(total_stmt) or 0
    transaction_stmt = (
        select(TransactionModel)
        .where(*filters)
        .order_by(TransactionModel.transaction_date.desc())
        .offset((request.page - 1) * request.page_size)
        .limit(request.page_size)
    )
    items = (await db.scalars(transaction_stmt)).all()
    return {
        "items": items,
        "total": total,
        "page": request.page,
        "page_size": request.page_size,
    }


@router.put("/{transaction_id}", name="Обновить транзакцию", response_model=TransactionSchema)
async def update_transaction(transaction_id: int,
                             transaction: TransactionUpdateSchema,
                             db: AsyncSession = Depends(get_async_db),
                             current_user: UserModel = Depends(get_current_member),
                             ) -> TransactionSchema:
    """Обновление транзакции"""
    result = await db.scalars(
        select(TransactionModel).where(TransactionModel.id == transaction_id),
    )
    db_transaction = result.first()
    if db_transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Транзакция не найдена",
        )
    if db_transaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для обновления транзакции",
        )
    await db.execute(
        update(TransactionModel)
        .where(TransactionModel.id == transaction_id)
        .values(**transaction.model_dump()),
    )
    await update_account_balance(db, transaction.account_id)
    await db.refresh(db_transaction)
    return db_transaction


@router.delete("/{transaction_id}",
               name="Удалить транзакцию",
               response_model=TransactionSchema)
async def delete_transaction(transaction_id: int,
                             db: AsyncSession = Depends(get_async_db),
                             current_user: UserModel = Depends(get_current_member),
                             ) -> TransactionSchema:
    """Удаление транзакции"""
    result = await db.scalars(
        select(TransactionModel).where(TransactionModel.id == transaction_id,
                                       TransactionModel.is_active.is_(True)),
    )
    transaction = result.first()
    if transaction is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Транзакция не найдена",
        )

    if transaction.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав для удаления транзакции",
        )

    transaction.is_active = False
    await update_account_balance(db, transaction.account_id)
    await db.refresh(transaction)
    return transaction
