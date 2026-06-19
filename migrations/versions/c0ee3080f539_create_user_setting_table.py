"""create user setting table

Revision ID: c0ee3080f539
Revises: 655305000efa
Create Date: 2026-06-18 13:19:19.014554

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c0ee3080f539"
down_revision: Union[str, Sequence[str], None] = "655305000efa"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        """CREATE TABLE IF NOT EXISTS tripin_auth.user_settings (
          user_id             INTEGER PRIMARY KEY REFERENCES tripin_auth.userdata(id) ON DELETE CASCADE,
          has_seen_onboarding BOOLEAN NOT NULL DEFAULT FALSE,
          language            VARCHAR(10) NOT NULL DEFAULT 'en',
          updated_at          TIMESTAMP NOT NULL DEFAULT NOW()
        );"""
    )
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""DROP TABLE tripin_auth.user_settings;""")
    pass
