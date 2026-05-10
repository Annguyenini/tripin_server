"""refractor trip_contents

Revision ID: 0699493f39b5
Revises: a76c6fe5af3f
Create Date: 2026-05-09 21:42:35.679404

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0699493f39b5"
down_revision: Union[str, Sequence[str], None] = "a76c6fe5af3f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TYPE IF NOT EXISTS tripin_trips.content_events AS ENUM ('add','remove');
        CREATE TABLE IF NOT EXISTS tripin_trips.content_cards (
        id SERIAL PRIMARY KEY,
        trip_id INTEGER NOT NULL REFERENCES tripin_trips.trips_table(id) ON DELETE CASCADE,
        media_type TEXT DEFAULT NULL,
        media_path TEXT DEFAULT NULL,
        time_stamp TIMESTAMPTZ NOT NULL DEFAULT NOW(),
        modified_time TIMESTAMPTZ DEFAULT NOW(),
        media_id TEXT DEFAULT NULL,
        uuid TEXT NOT NULL,
        event tripin_trips.content_events DEFAULT 'add',
        altitude REAL DEFAULT NULL,
        latitude REAL DEFAULT NULL,
        longitude REAL DEFAULT NULL,
        speed REAL DEFAULT NULL,
        heading REAL DEFAULT NULL,
        city TEXT DEFAULT NULL,
        region TEXT DEFAULT NULL,
        country TEXT DEFAULT NULL,
        iso_country_code TEXT DEFAULT NULL,
        )
        """)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DROP TYPE IF EXISTS tripin_trips.content_events;
        DROP TABLE IF EXISTS tripin_trips.content_cards;
        """)
    pass
