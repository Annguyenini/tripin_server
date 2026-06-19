"""create trigger function for user settings

Revision ID: b199a388b364
Revises: c0ee3080f539
Create Date: 2026-06-18 13:23:26.532128

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b199a388b364"
down_revision: Union[str, Sequence[str], None] = "c0ee3080f539"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE OR REPLACE FUNCTION tripin_auth.create_user_settings()
        RETURNS TRIGGER AS $$
        BEGIN
          INSERT INTO tripin_auth.user_settings (user_id) VALUES (NEW.id);
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;""")
    op.execute("""
        CREATE TRIGGER on_user_created
        AFTER INSERT ON tripin_auth.userdata
        FOR EACH ROW EXECUTE FUNCTION tripin_auth.create_user_settings();
        """)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
