"""add role to token

Revision ID: 15f922fd8223
Revises: 7398b77c2ea6
Create Date: 2026-04-05 17:30:38.815974

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '15f922fd8223'
down_revision: Union[str, Sequence[str], None] = '7398b77c2ea6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(f'''
               ALTER TABLE tripin_auth.tokens ADD COLUMN IF NOT EXISTS role TEXT NOT NULL DEFAULT 'user';
               ''')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(f'''
            ALTER TABLE tripin_auth.tokens DROP COLUMN IF EXISTS role;
            ''')

    pass
