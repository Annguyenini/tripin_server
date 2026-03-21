"""empty message

Revision ID: c69b2cb1acdf
Revises: 64426693b432
Create Date: 2026-03-20 13:26:09.256788

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c69b2cb1acdf'
down_revision: Union[str, Sequence[str], None] = '64426693b432'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
