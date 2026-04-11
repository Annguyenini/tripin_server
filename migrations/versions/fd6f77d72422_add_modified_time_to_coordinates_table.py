"""add modified_time to coordinates table

Revision ID: fd6f77d72422
Revises: 950b6c81be1d
Create Date: 2026-04-10 19:01:29.271628

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fd6f77d72422'
down_revision: Union[str, Sequence[str], None] = '950b6c81be1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(f'''
    ALTER TABLE tripin_trips.trip_coordinates ADD COLUMN IF NOT EXISTS modified_time BIGINT DEFAULT 0 NOT NULL;
''')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(f'''
    ALTER TABLE tripin_trips.trip_coordinates DROP COLUMN modified_time IF EXISTS;
''')
    pass
