"""rename type to transaction_type in transactions

Revision ID: 78b86bf46c78
Revises: c5024cce91cf
Create Date: 2026-06-16 18:12:49.813560

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '78b86bf46c78'
down_revision: Union[str, Sequence[str], None] = 'c5024cce91cf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Если колонка уже называлась `type`, то переименовываем её
    op.alter_column(
        "transactions",
        "type",
        new_column_name="transaction_type",
        existing_type=sa.String(),  # или другой тип — укажи правильно!
        existing_nullable=False
    )

def downgrade() -> None:
    op.alter_column(
        "transactions",
        "transaction_type",
        new_column_name="type",
        existing_type=sa.String(),
        existing_nullable=False
    )
