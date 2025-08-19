"""merge_tiktok_and_media_branches

Revision ID: af25eb8630d0
Revises: 11acbb169f19, add_instance_media
Create Date: 2025-08-18 22:59:40.966163

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'af25eb8630d0'
down_revision: Union[str, Sequence[str], None] = ('11acbb169f19', 'add_instance_media')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
