"""fill in existing user for user settings

Revision ID: 99ca280536cc
Revises: b199a388b364
Create Date: 2026-06-18 13:28:59.267524

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "99ca280536cc"
down_revision: Union[str, Sequence[str], None] = "b199a388b364"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        INSERT INTO tripin_auth.user_settings (user_id)
        SELECT id FROM tripin_auth.userdata u
        WHERE NOT EXISTS (
          SELECT 1 FROM tripin_auth.user_settings s WHERE s.user_id = u.id
        );""")
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
