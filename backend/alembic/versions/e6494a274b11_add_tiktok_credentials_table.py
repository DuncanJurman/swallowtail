"""add_tiktok_credentials_table

Revision ID: e6494a274b11
Revises: eb21841da08c
Create Date: 2025-07-29 23:21:00.926465

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'e6494a274b11'
down_revision: Union[str, Sequence[str], None] = 'eb21841da08c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create TikTok credentials table for storing OAuth tokens."""
    op.create_table(
        'instance_tiktok_credentials',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('instance_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('tiktok_open_id', sa.String(length=255), nullable=False),
        sa.Column('tiktok_union_id', sa.String(length=255), nullable=True),
        sa.Column('display_name', sa.String(length=255), nullable=False),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('access_token', sa.Text(), nullable=False),
        sa.Column('refresh_token', sa.Text(), nullable=False),
        sa.Column('access_token_expires_at', sa.DateTime(), nullable=False),
        sa.Column('refresh_token_expires_at', sa.DateTime(), nullable=False),
        sa.Column('scopes', sa.JSON(), nullable=False),
        sa.Column('user_info', sa.JSON(), nullable=True),
        sa.Column('is_active', sa.String(length=20), nullable=False, server_default='active'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['instance_id'], ['instances.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('instance_id'),
        sa.UniqueConstraint('tiktok_open_id')
    )
    
    # Create indexes
    op.create_index('idx_tiktok_credentials_instance', 'instance_tiktok_credentials', ['instance_id'], unique=False)
    op.create_index('idx_tiktok_credentials_open_id', 'instance_tiktok_credentials', ['tiktok_open_id'], unique=False)
    op.create_index('idx_tiktok_credentials_expires', 'instance_tiktok_credentials', ['access_token_expires_at'], unique=False)


def downgrade() -> None:
    """Drop TikTok credentials table."""
    op.drop_index('idx_tiktok_credentials_expires', table_name='instance_tiktok_credentials')
    op.drop_index('idx_tiktok_credentials_open_id', table_name='instance_tiktok_credentials')
    op.drop_index('idx_tiktok_credentials_instance', table_name='instance_tiktok_credentials')
    op.drop_table('instance_tiktok_credentials')
