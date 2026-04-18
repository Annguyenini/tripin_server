"""fix tokens table

Revision ID: af615c6cd557
Revises: fd6f77d72422
Create Date: 2026-04-16 14:54:52.968775

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af615c6cd557'
down_revision: Union[str, Sequence[str], None] = 'fd6f77d72422'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(f'''
   
    DO $$ 
    BEGIN
        IF EXISTS(
               SELECT 1 FROM information_schema.columns
               WHERE table_schema = 'tripin_auth'
               AND table_name = 'tokens'
               AND column_name = 'expires_at') 
        THEN 
            ALTER TABLE tripin_auth.tokens RENAME COLUMN expires_at TO expired_at;
        END IF;
    END $$;
''')
    pass


def downgrade() -> None:
    """Downgrade schema."""
    op.execute(f'''
     DO $$ 
    BEGIN
        IF EXISTS(
               SELECT 1 FROM information_schema.columns
               WHERE table_schema = 'tripin_auth'
               AND table_name = 'tokens'
               AND column_name = 'expired_at') 
        THEN 
            ALTER TABLE tripin_auth.tokens RENAME COLUMN expired_at TO expires_at;
        END IF;
    END $$;
''')

    pass
