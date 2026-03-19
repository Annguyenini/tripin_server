"""empty message

Revision ID: 64426693b432
Revises: 57904729d8f7
Create Date: 2026-03-16 08:42:55.649168

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '64426693b432'
down_revision: Union[str, Sequence[str], None] = '57904729d8f7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('ALTER TABLE tripin_trips.trip_medias ADD COLUMN IF NOT EXISTS media_id TEXT;')
    op.execute('ALTER TABLE tripin_trips.trip_medias DROP COLUMN IF EXISTS version;')


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('ALTER TABLE tripin_trips.trip_medias DROP COLUMN IF EXISTS media_id;')
    op.execute('ALTER TABLE tripin_trips.trip_medias ADD COLUMN IF NOT EXISTS version BIGINT;')
