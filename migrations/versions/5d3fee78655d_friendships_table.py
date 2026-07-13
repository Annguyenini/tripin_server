"""friendships table

Revision ID: 5d3fee78655d
Revises: 99ca280536cc
Create Date: 2026-07-02 13:59:16.420014

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5d3fee78655d"
down_revision: Union[str, Sequence[str], None] = "99ca280536cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("""
        CREATE SCHEMA IF NOT EXISTS tripin_friendships;
        """)
    op.execute("""
        CREATE TYPE tripin_friendships.friendships_status AS ENUM ('REQ_1','REQ_2','FRIEND');
        """)

    op.execute("""
        CREATE TABLE IF NOT EXISTS tripin_friendships.friendships_table(
        user_id1 INTEGER NOT NULL,
        user_id2 INTEGER NOT NULL,
        status tripin_friendships.friendships_status NOT NULL,
        last_update TIMESTAMPTZ DEFAULT NOW()
        );
        """)
    op.execute("""
        ALTER TABLE tripin_friendships.friendships_table ADD CONSTRAINT user_order_check CHECK (user_id1<user_id2);
        """)
    op.execute("""
        ALTER TABLE tripin_friendships.friendships_table ADD CONSTRAINT friend_ship_unique UNIQUE (user_id1,user_id2);
        """)
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("""
        DROP SCHEMA IF EXISTS tripin_friendships;
        """)

    op.execute("""
        DROP TYPE IF EXISTS tripin_friendships.friendships_status;
        """)

    op.execute("""
        DROP TABLE IF EXISTS tripin_friendships.friendships_table
        """)
    op.execute("""
        ALTER TABLE tripin_friendships.friendships_table DROP CONSTRAINT user_order_check;
        """)
    op.execute("""
        ALTER TABLE tripin_friendships.friendships_table DROP CONSTRAINT friend_ship_unique;
        """)
    pass
