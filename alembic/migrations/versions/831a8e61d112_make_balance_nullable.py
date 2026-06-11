"""make balance nullable

Revision ID: 831a8e61d112
Revises: b2107ba1c6ea
Create Date: 2026-06-11 15:32:38.109156

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '831a8e61d112'
down_revision: Union[str, Sequence[str], None] = 'b2107ba1c6ea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Указываем тип явно, чтобы избежать ошибок (尤其 в PostgreSQL)
    op.alter_column(
        'accounts', 
        'balance',
        existing_type=sa.DECIMAL(precision=10, scale=2),
        nullable=True,
        existing_nullable=False,  # ← текущее состояние
        server_default=sa.text('NULL')  # ← явно ставим NULL как default
    )


def downgrade() -> None:
    op.alter_column(
        'accounts',
        'balance',
        existing_type=sa.DECIMAL(precision=10, scale=2),
        nullable=False,
        existing_nullable=True,
        server_default=sa.text('0.0')  # ← возвращаем старый default (если был)
    )