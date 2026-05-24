"""add event to trips table

Revision ID: a76c6fe5af3f
Revises: 49dc4485af6e
Create Date: 2026-05-08 21:01:25.560986

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "a76c6fe5af3f"
down_revision: Union[str, Sequence[str], None] = "49dc4485af6e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TYPE tripin_trips.trip_event AS ENUM ('add','remove');
        ALTER TABLE tripin_trips.trips_table ADD COLUMN IF NOT EXISTS event tripin_trips.trip_event NOT NULL DEFAULT 'add';
        """)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DELETE TYPE tripin_trips.trip_event;
        ALTER TABLE tripin_trips.trips_table DROP COLUMN IF EXISTS event ;
        """)
    pass
