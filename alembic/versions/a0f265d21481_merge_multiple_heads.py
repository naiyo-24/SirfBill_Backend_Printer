"""Merge multiple heads

Revision ID: a0f265d21481
Revises: 0ad6cc2eae7f, 57239e200060
Create Date: 2026-10-01 14:16:35.406861

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a0f265d21481'
down_revision: Union[str, Sequence[str], None] = ('0ad6cc2eae7f', '57239e200060')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
