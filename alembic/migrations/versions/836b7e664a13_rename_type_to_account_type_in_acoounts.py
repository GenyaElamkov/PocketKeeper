"""rename type to account_type in acoounts

Revision ID: 836b7e664a13
Revises: 78b86bf46c78
Create Date: 2026-06-16 18:15:33.807182

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '836b7e664a13'
down_revision: Union[str, Sequence[str], None] = '78b86bf46c78'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Если колонка уже называлась `type`, то переименовываем её
    op.alter_column(
        "accounts",
        "type",
        new_column_name="account_type",
        existing_type=sa.String(),  # или другой тип — укажи правильно!
        existing_nullable=False
    )

def downgrade() -> None:
    op.alter_column(
        "accounts",
        "account_type",
        new_column_name="type",
        existing_type=sa.String(),
        existing_nullable=False
    )
