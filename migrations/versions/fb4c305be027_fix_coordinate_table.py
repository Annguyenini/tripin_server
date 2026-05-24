"""fix coordinate table

Revision ID: fb4c305be027
Revises: af615c6cd557
Create Date: 2026-04-16 15:58:24.043626

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy import text

# revision identifiers, used by Alembic.
revision: str = "fb4c305be027"
down_revision: Union[str, Sequence[str], None] = "af615c6cd557"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    pass


def downgrade() -> None:

    pass
