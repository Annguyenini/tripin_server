"""update trip media

Revision ID: 950b6c81be1d
Revises: beea5d1d8a20
Create Date: 2026-04-08 19:09:55.835673

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '950b6c81be1d'
down_revision: Union[str, Sequence[str], None] = 'beea5d1d8a20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('''
UPDATE tripin_trips.trip_medias SET media_type = 'photo' WHERE media_type = 'image';
''')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('''
UPDATE tripin_trips.trip_medias SET media_type = 'image' WHERE media_type = 'photo';
''')
    pass
