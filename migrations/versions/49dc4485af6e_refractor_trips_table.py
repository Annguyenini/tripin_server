"""refractor trips table

Revision ID: 49dc4485af6e
Revises: d7f6088373ef
Create Date: 2026-05-04 21:39:53.423052

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "49dc4485af6e"
down_revision: Union[str, Sequence[str], None] = "d7f6088373ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        ALTER TABLE tripin_trips.trips_table DROP COLUMN IF EXISTS etag;
        ALTER TABLE tripin_trips.trips_table DROP COLUMN IF EXISTS trip_coordinates_version;
        ALTER TABLE tripin_trips.trips_table DROP COLUMN IF EXISTS trip_medias_version;
        ALTER TABLE tripin_trips.trips_table DROP COLUMN IF EXISTS trip_informations_version;
        ALTER TABLE tripin_trips.trips_table ADD COLUMN IF NOT EXISTS modified_time TIMESTAMPTZ;
        ALTER TABLE tripin_trips.trips_table ADD COLUMN IF NOT EXISTS content_modified_time TIMESTAMPTZ;
        """)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(
        """
        ALTER TABLE tripin_trips.trips_table ADD COLUMN IF NOT EXISTS etag TEXT;
        ALTER TABLE tripin_trips.trips_table ADD COLUMN IF NOT EXISTS trip_coordinates_version BIGINT;
        ALTER TABLE tripin_trips.trips_table ADD COLUMN IF NOT EXISTS trip_medias_version BIGINT;
        ALTER TABLE tripin_trips.trips_table ADD COLUMN IF NOT EXISTS trip_informations_version BIGINT;
        ALTER TABLE tripin_trips.trips_table DROP COLUMN IF EXISTS modified_time;
        ALTER TABLE tripin_trips.trips_table DROP COLUMN IF EXISTS content_modified_time;
        """
    )
    pass
