"""add_tiktok_posting_fields_to_tasks

Revision ID: 11acbb169f19
Revises: fix_timezone_tiktok
Create Date: 2025-08-12 00:16:06.682802

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '11acbb169f19'
down_revision: Union[str, Sequence[str], None] = 'fix_timezone_tiktok'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add TikTok posting fields to instance_tasks table."""
    # Add TikTok posting fields
    op.add_column('instance_tasks', 
        sa.Column('tiktok_post_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('instance_tasks', 
        sa.Column('tiktok_publish_id', sa.String(length=255), nullable=True))
    op.add_column('instance_tasks', 
        sa.Column('tiktok_post_status', sa.String(length=50), nullable=True))
    op.add_column('instance_tasks', 
        sa.Column('tiktok_post_url', sa.String(length=500), nullable=True))
    op.add_column('instance_tasks', 
        sa.Column('scheduled_post_time', sa.DateTime(), nullable=True))


def downgrade() -> None:
    """Remove TikTok posting fields from instance_tasks table."""
    op.drop_column('instance_tasks', 'scheduled_post_time')
    op.drop_column('instance_tasks', 'tiktok_post_url')
    op.drop_column('instance_tasks', 'tiktok_post_status')
    op.drop_column('instance_tasks', 'tiktok_publish_id')
    op.drop_column('instance_tasks', 'tiktok_post_data')
