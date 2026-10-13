"""Merge multiple heads

Revision ID: 9fd5c43cc9e1
Revises: 725821f0e7ce, da64ff00d021
Create Date: 2026-09-28 17:41:10.917117

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9fd5c43cc9e1'
down_revision: Union[str, Sequence[str], None] = ('725821f0e7ce', 'da64ff00d021')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
