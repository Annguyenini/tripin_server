"""add location data to image

Revision ID: f9bfc5a2fd16
Revises: fad2f97e4e2d
Create Date: 2026-04-20 16:46:42.782184

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f9bfc5a2fd16'
down_revision: Union[str, Sequence[str], None] = 'fad2f97e4e2d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(f'''
    ALTER TABLE tripin_trips.trip_medias ADD COLUMN IF NOT EXISTS city TEXT DEFAULT null;
    ALTER TABLE tripin_trips.trip_medias ADD COLUMN IF NOT EXISTS region TEXT DEFAULT null;
    ALTER TABLE tripin_trips.trip_medias ADD COLUMN IF NOT EXISTS country TEXT DEFAULT null;
    ALTER TABLE tripin_trips.trip_medias ADD COLUMN IF NOT EXISTS iso_country_code TEXT DEFAULT null;
''')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(f'''
    ALTER TABLE tripin_trips.trip_medias DROP COLUMN IF EXISTS city;
    ALTER TABLE tripin_trips.trip_medias DROP COLUMN IF EXISTS region;
    ALTER TABLE tripin_trips.trip_medias DROP COLUMN IF EXISTS country;
    ALTER TABLE tripin_trips.trip_medias DROP COLUMN IF EXISTS iso_country_code;
''')
    pass
