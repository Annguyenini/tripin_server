"""modify trip_medias table

Revision ID: beea5d1d8a20
Revises: 15f922fd8223
Create Date: 2026-04-07 10:05:30.942911

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'beea5d1d8a20'
down_revision: Union[str, Sequence[str], None] = '15f922fd8223'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute ('''
                CREATE TYPE tripin_trips.media_events AS ENUM ('add','remove');
                ALTER TABLE tripin_trips.trip_medias ADD COLUMN IF NOT EXISTS event tripin_trips.media_events NOT NULL DEFAULT 'add';
                ''')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('''
               DROP TYPE tripin_trips.media_events;
               ALTER TABLE tripin_trips.trip_medias DROP COLUMN IF EXISTS event;
               ''')
    pass
