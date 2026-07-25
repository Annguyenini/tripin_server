"""add devices table

Revision ID: 52a07921d329
Revises: 2cf8d243b66c
Create Date: 2026-07-20 22:09:54.525387

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '52a07921d329'
down_revision: Union[str, Sequence[str], None] = '2cf8d243b66c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute('''
        CREATE TABLE IF NOT EXISTS tripin_auth.devices (
            id SERIAL PRIMARY KEY,
            user_id INTEGER NOT NULL REFERENCES tripin_auth.userdata(id) ON DELETE CASCADE,
            device_id TEXT NOT NULL UNIQUE,
            push_token TEXT DEFAULT NULL UNIQUE,
            platform TEXT NOT NULL,
            last_seen TIMESTAMPTZ DEFAULT NOW()
        );
        ''')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute('''
        DROP TABLE IF EXISTS tripin_auth.devices;
        ''')
    pass
