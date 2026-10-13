"""Merge multiple heads

Revision ID: 57239e200060
Revises: 7536d9dccdf8, 9a459c4b2eb6
Create Date: 2026-09-30 14:47:26.134389

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '57239e200060'
down_revision: Union[str, Sequence[str], None] = ('7536d9dccdf8', '9a459c4b2eb6')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
