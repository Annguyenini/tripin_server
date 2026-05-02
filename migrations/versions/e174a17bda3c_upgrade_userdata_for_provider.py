"""upgrade userdata for provider

Revision ID: e174a17bda3c
Revises: f9bfc5a2fd16
Create Date: 2026-04-25 11:58:51.776207

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e174a17bda3c'
down_revision: Union[str, Sequence[str], None] = 'f9bfc5a2fd16'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(f'''
    ALTER TABLE tripin_auth.userdata ADD COLUMN IF NOT EXISTS provider TEXT DEFAULT null;
    ALTER TABLE tripin_auth.userdata ADD COLUMN IF NOT EXISTS provider_id TEXT DEFAULT null;
    
''')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(f'''
    ALTER TABLE tripin_auth.userdata DROP COLUMN IF EXISTS provider;
    ALTER TABLE tripin_auth.userdata DROP COLUMN IF EXISTS provider_id;
    
''')
    pass
