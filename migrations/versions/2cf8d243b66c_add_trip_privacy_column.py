"""add trip privacy column

Revision ID: 2cf8d243b66c
Revises: 5d3fee78655d
Create Date: 2026-07-02 14:03:26.200855

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "2cf8d243b66c"
down_revision: Union[str, Sequence[str], None] = "5d3fee78655d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TYPE tripin_trips.trip_privacy AS ENUM ('public','friend','private');
        """)
    op.execute("""
        ALTER TABLE tripin_trips.trips_table ADD COLUMN IF NOT EXISTS privacy tripin_trips.trip_privacy DEFAULT 'private';
        """)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DROP TYPE IF EXISTS tripin_trips.trip_privacy;
        """)
    op.execute("""
        ALTER TABLE tripin_trips.trips_table DROP COLUMN IF EXISTS privacy;
        """)

    pass
