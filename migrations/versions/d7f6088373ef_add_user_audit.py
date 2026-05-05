"""add user_audit

Revision ID: d7f6088373ef
Revises: d2fef24912ca
Create Date: 2026-05-02 11:07:53.028489

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "d7f6088373ef"
down_revision: Union[str, Sequence[str], None] = "d2fef24912ca"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE TYPE tripin_auth.role AS ENUM ('user','admin');
        CREATE TYPE tripin_auth.user_audit_action AS ENUM ('reset_password','change_displayname','change_avatar');
        CREATE TABLE IF NOT EXISTS tripin_auth.user_audit(
        id SERIAL PRIMARY KEY,
        user_id INT NOT NULL REFERENCES tripin_auth.userdata (id) ON DELETE CASCADE,
        modified_time TIMESTAMPTZ DEFAULT NOW(),
        action tripin_auth.user_audit_action NOT NULL,
        ip_address TEXT NOT NULL,
        new_value TEXT,
        old_value TEXT
        )
        """)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DROP TYPE tripin_auth.role;
        DROP TYPE tripin_auth.user_audit_action ;
        DROP TABLE IF EXISTS tripin_auth.user_audit;
        """)
    pass
