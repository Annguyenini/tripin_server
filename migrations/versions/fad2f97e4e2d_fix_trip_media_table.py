"""fix trip media table

Revision ID: fad2f97e4e2d
Revises: 427e63b06dea
Create Date: 2026-04-16 20:09:13.400793

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fad2f97e4e2d'
down_revision: Union[str, Sequence[str], None] = '427e63b06dea'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(f'''

DO $$ 
    BEGIN
        IF EXISTS(
               SELECT 1 FROM information_schema.columns
               WHERE table_schema = 'tripin_trips'
               AND table_name = 'trip_medias'
               AND column_name = 'key') 
        THEN 
            ALTER TABLE tripin_trips.trip_medias RENAME COLUMN key TO media_path;
        END IF;
    END $$;
''')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(f'''

DO $$ 
    BEGIN
        IF EXISTS(
               SELECT 1 FROM information_schema.columns
               WHERE table_schema = 'tripin_trips'
               AND table_name = 'trip_medias'
               AND column_name = 'media_path') 
        THEN 
            ALTER TABLE tripin_trips.trip_medias RENAME COLUMN media_path TO key;
        END IF;
    END $$;
''')
    pass
