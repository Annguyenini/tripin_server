"""modify userdata, tokens tables

Revision ID: d4beb4a0f4f6
Revises: 0699493f39b5
Create Date: 2026-05-16 22:46:41.082395

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d4beb4a0f4f6"
down_revision: Union[str, Sequence[str], None] = "0699493f39b5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        ALTER TABLE tripin_auth.userdata ALTER COLUMN created_time TYPE timestamptz USING created_time AT TIME ZONE 'UTC'
                """)
    op.execute("""
        ALTER TABLE tripin_auth.tokens ALTER COLUMN issued_at TYPE timestamptz USING issued_at AT TIME ZONE 'UTC'
        """)
    op.execute("""
        ALTER TABLE tripin_auth.tokens ALTER COLUMN expired_at TYPE timestamptz USING expired_at AT TIME ZONE 'UTC'
        """)

    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        ALTER TABLE tripin_auth.userdata ALTER COLUMN created_time TYPE timestamp USING created_time AT TIME ZONE 'UTC'
        """)
    op.execute("""
        ALTER TABLE tripin_auth.tokens ALTER COLUMN issued_at TYPE timestamp USING issued_at AT TIME ZONE 'UTC'
        """)
    op.execute("""
        ALTER TABLE tripin_auth.tokens ALTER COLUMN expired_at TYPE timestamp USING expired_at AT TIME ZONE 'UTC'

        """)
    pass
