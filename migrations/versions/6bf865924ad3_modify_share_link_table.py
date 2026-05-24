"""modify share link table

Revision ID: 6bf865924ad3
Revises: d4beb4a0f4f6
Create Date: 2026-05-22 17:31:35.824688

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6bf865924ad3"
down_revision: Union[str, Sequence[str], None] = "d4beb4a0f4f6"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        ALTER TABLE tripin_trips.trip_shared_links ALTER COLUMN created_time TYPE timestamptz USING to_timestamp(created_time/1000);
        ALTER TABLE tripin_trips.trip_shared_links ALTER COLUMN expired_time TYPE timestamptz USING to_timestamp(expired_time/1000);
        """)

    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        ALTER TABLE tripin_trips.trip_shared_links ALTER COLUMN created_time TYPE BIGINT USING (EXTRACT(EPOCH FROM created_time) * 1000)::bigint;
        ALTER TABLE tripin_trips.trip_shared_links ALTER COLUMN expired_time TYPE BIGINT USING (EXTRACT(EPOCH FROM expired_time) * 1000)::bigint;
        """)
    pass
