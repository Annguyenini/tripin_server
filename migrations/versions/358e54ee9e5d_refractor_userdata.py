"""refractor userdata

Revision ID: 358e54ee9e5d
Revises: 5226bf61baf9
Create Date: 2026-05-02 10:35:58.451562

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "358e54ee9e5d"
down_revision: Union[str, Sequence[str], None] = "5226bf61baf9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        ALTER TABLE tripin_auth.userdata DROP COLUMN IF EXISTS etag ;
        ALTER TABLE tripin_auth.userdata DROP COLUMN IF EXISTS trips_data_version ;
        ALTER TABLE tripin_auth.userdata DROP COLUMN IF EXISTS trips_data_etag ;
        ALTER TABLE tripin_auth.userdata DROP COLUMN IF EXISTS userdata_version ;
        ALTER TABLE tripin_auth.userdata ADD COLUMN IF NOT EXISTS modified_time TIMESTAMPTZ DEFAULT NOW();
        ALTER TABLE tripin_auth.userdata ADD COLUMN IF NOT EXISTS trips_modified_time TIMESTAMPTZ DEFAULT NOW();
        """)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        ALTER TABLE tripin_auth.userdata ADD COLUMN IF NOT EXISTS etag TEXT;
        ALTER TABLE tripin_auth.userdata ADD COLUMN IF NOT EXISTS trips_data_version TEXT;
        ALTER TABLE tripin_auth.userdata ADD COLUMN IF NOT EXISTS trips_data_etag TEXT;
        ALTER TABLE tripin_auth.userdata ADD COLUMN IF NOT EXISTS userdata_version TEXT;
        ALTER TABLE tripin_auth.userdata DROP COLUMN IF EXISTS modified_time;
        ALTER TABLE tripin_auth.userdata DROP COLUMN IF EXISTS trips_modified_time;
        """)
    pass
