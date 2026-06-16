"""Add indexes to transactions table

Revision ID: c5024cce91cf
Revises: 831a8e61d112
Create Date: 2026-06-16 17:51:48.332866

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5024cce91cf'
down_revision: Union[str, Sequence[str], None] = '831a8e61d112'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_index(
        "ix_transactions_user_id",
        "transactions",
        ["user_id"],
        unique=False,
    )
    op.create_index(
        "ix_transactions_account_id",
        "transactions",
        ["account_id"],
        unique=False,
    )
    op.create_index(
        "ix_transactions_category_id",
        "transactions",
        ["category_id"],
        unique=False,
    )
    op.create_index(
        "ix_transactions_transaction_date",
        "transactions",
        ["transaction_date"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_transactions_user_id", table_name="transactions")
    op.drop_index("ix_transactions_account_id", table_name="transactions")
    op.drop_index("ix_transactions_category_id", table_name="transactions")
    op.drop_index("ix_transactions_transaction_date", table_name="transactions")
