"""trip coordinate modify

Revision ID: f6758b67c795
Revises: ba5b779ca0b1
Create Date: 2026-03-23 19:25:43.978825

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f6758b67c795'
down_revision: Union[str, Sequence[str], None] = 'ba5b779ca0b1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        '''
        ALTER TABLE tripin_trips.trip_coordinates DROP COLUMN IF EXISTS event_id;
        ALTER TABLE tripin_trips.trip_coordinates ADD COLUMN IF NOT EXISTS coordinate_id TEXT DEFAULT NULL;
        '''
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        '''
        ALTER TABLE tripin_trips.trip_coordinates ADD COLUMN IF NOT EXISTS event_id BIGINT NOT NULL DEFAULT 0;
        ALTER TABLE tripin_trips.trip_coordinates DROP COLUMN IF EXISTS coordinate_id;
        '''
    )
    pass
