"""drop not null for tokens

Revision ID: 5226bf61baf9
Revises: e174a17bda3c
Create Date: 2026-04-26 22:58:07.155472

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5226bf61baf9'
down_revision: Union[str, Sequence[str], None] = 'e174a17bda3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(f'''
ALTER TABLE tripin_auth.tokens ALTER COLUMN user_name DROP NOT NULL''')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(f'''
ALTER TABLE tripin_auth.tokens ALTER COLUMN user_name DEFAULT NOT NULL''')
    pass
