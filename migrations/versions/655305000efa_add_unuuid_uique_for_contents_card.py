"""add unuuid uique for contents card

Revision ID: 655305000efa
Revises: 6bf865924ad3
Create Date: 2026-06-09 15:35:03.750117

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "655305000efa"
down_revision: Union[str, Sequence[str], None] = "6bf865924ad3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        DELETE FROM tripin_trips.content_cards
        WHERE id NOT IN (
            SELECT MAX(id)
            FROM tripin_trips.content_cards
            GROUP BY uuid
        );
        ALTER TABLE tripin_trips.content_cards
        ADD CONSTRAINT content_cards_uuid_unique UNIQUE (uuid);
        """)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
