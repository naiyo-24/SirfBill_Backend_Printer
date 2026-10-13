"""Merge multiple heads

Revision ID: 9a459c4b2eb6
Revises: 83c511ba5384, 9fd5c43cc9e1
Create Date: 2026-09-29 17:12:20.689321

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a459c4b2eb6'
down_revision: Union[str, Sequence[str], None] = ('83c511ba5384', '9fd5c43cc9e1')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
