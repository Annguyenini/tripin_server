"""refractor tokens

Revision ID: d2fef24912ca
Revises: 358e54ee9e5d
Create Date: 2026-05-02 11:00:31.812460

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d2fef24912ca"
down_revision: Union[str, Sequence[str], None] = "358e54ee9e5d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        ALTER TABLE tripin_auth.tokens DROP COLUMN IF EXISTS user_name ;
        ALTER TABLE tripin_auth.tokens ADD COLUMN IF NOT EXISTS device_id TEXT ;
        ALTER TABLE tripin_auth.tokens ADD COLUMN IF NOT EXISTS last_used TIMESTAMPTZ;
        """)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        ALTER TABLE tripin_auth.tokens ADD COLUMN IF NOT EXISTS user_name TEXT;
        ALTER TABLE tripin_auth.tokens DROP COLUMN IF EXISTS device_id;
        ALTER TABLE tripin_auth.tokens DROP COLUMN IF EXISTS last_used;
        """)
    pass
