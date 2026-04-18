"""fix coordinate table

Revision ID: fb4c305be027
Revises: af615c6cd557
Create Date: 2026-04-16 15:58:24.043626

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fb4c305be027'
down_revision: Union[str, Sequence[str], None] = 'af615c6cd557'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('''
    ALTER TABLE tripin_trips.trip_medias 
    ALTER COLUMN time_stamp TYPE BIGINT 
    USING time_stamp;

        ''')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('''
    ALTER TABLE tripin_trips.trip_coordinates 
    ALTER COLUMN time_stamp TYPE TIMESTAMP 
    USING BIGINT;
''')
    pass
