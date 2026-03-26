"""empty message

Revision ID: ba5b779ca0b1
Revises: c69b2cb1acdf
Create Date: 2026-03-21 11:37:57.069901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'ba5b779ca0b1'
down_revision: Union[str, Sequence[str], None] = 'c69b2cb1acdf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('''
    CREATE TYPE tripin_trips.coordinates_events AS ENUM ('add','remove');
    ALTER TABLE tripin_trips.trip_coordinates ADD COLUMN IF NOT EXISTS event_id BIGINT DEFAULT 0 NOT NULL;
    ALTER TABLE tripin_trips.trip_coordinates ADD COLUMN IF NOT EXISTS event tripin_trips.coordinates_events DEFAULT 'add' NOT NULLQQ;    
    ''')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('''
    ALTER TABLE tripin_trips.trip_coordinates DROP COLUMN IF EXISTS event_id;
    ALTER TABLE tripin_trips.trip_coordinates DROP COLUMN IF EXISTS event;
    DROP TYPEQ IF EXISTS tripin_trips.coordinates_events;

    ''')
    pass