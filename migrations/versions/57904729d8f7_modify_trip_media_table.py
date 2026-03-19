"""modify trip media table

Revision ID: 57904729d8f7
Revises: fef7dd216476
Create Date: 2026-03-15 21:44:34.447645

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '57904729d8f7'
down_revision: Union[str, Sequence[str], None] = 'fef7dd216476'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('ALTER TABLE tripin_trips.trip_medias ADD COLUMN IF NOT EXISTS modified_time BIGINT;')
    
def downgrade() -> None:
    """Downgrade schema."""
    op.execute('ALTER TABLE tripin_trips.trip_medias DROP COLUMN IF EXISTS modified_time;')
   