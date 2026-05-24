"""fix medias table

Revision ID: 427e63b06dea
Revises: fb4c305be027
Create Date: 2026-04-16 16:05:34.050693

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "427e63b06dea"
down_revision: Union[str, Sequence[str], None] = "fb4c305be027"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    pass


def downgrade() -> None:
    """Downgrade schema."""

    pass
