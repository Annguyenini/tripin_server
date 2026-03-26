"""add coordinate_id to trip media table

Revision ID: 7398b77c2ea6
Revises: f6758b67c795
Create Date: 2026-03-23 20:34:21.066410

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7398b77c2ea6'
down_revision: Union[str, Sequence[str], None] = 'f6758b67c795'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        '''
        ALTER TABLE tripin_trips.trip_medias ADD COLUMN IF NOT EXISTS coordinate_id TEXT DEFAULT NULL;
        '''
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        '''
        ALTER TABLE tripin_trips.trip_medias DROP COLUMN IF EXISTS coordinate_id ;

        '''
        
    )
    pass
