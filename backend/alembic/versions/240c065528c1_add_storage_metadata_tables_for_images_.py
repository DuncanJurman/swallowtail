"""Add storage metadata tables for images and videos

Revision ID: 240c065528c1
Revises: 6ab646c0b425
Create Date: 2025-07-15 01:24:41.750825

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '240c065528c1'
down_revision: Union[str, Sequence[str], None] = '6ab646c0b425'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Skip the auto-generated changes that are causing issues
    # We only care about creating the storage tables
    
    # Create image metadata table
    op.create_table('image_metadata',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('storage_path', sa.Text(), nullable=False),
        sa.Column('public_url', sa.Text(), nullable=False),
        sa.Column('cdn_url', sa.Text(), nullable=True),
        sa.Column('image_type', sa.String(length=50), nullable=False),
        sa.Column('sub_type', sa.String(length=50), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('width', sa.Integer(), nullable=True),
        sa.Column('height', sa.Integer(), nullable=True),
        sa.Column('format', sa.String(length=10), nullable=True),
        sa.Column('generation_session_id', sa.String(length=255), nullable=True),
        sa.Column('evaluation_score', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('storage_backend', sa.String(length=50), server_default='supabase', nullable=True),
        sa.Column('status', sa.String(length=50), server_default='active', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('last_accessed_at', sa.DateTime(), nullable=True),
        sa.Column('archived_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_images_product', 'image_metadata', ['product_id'], unique=False)
    op.create_index('idx_images_type', 'image_metadata', ['image_type', 'sub_type'], unique=False)
    op.create_index('idx_images_status', 'image_metadata', ['status'], unique=False)
    op.create_index('idx_images_accessed', 'image_metadata', ['last_accessed_at'], unique=False)
    
    # Create video metadata table
    op.create_table('video_metadata',
        sa.Column('id', postgresql.UUID(as_uuid=True), server_default=sa.text('gen_random_uuid()'), nullable=False),
        sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('storage_path', sa.Text(), nullable=False),
        sa.Column('public_url', sa.Text(), nullable=False),
        sa.Column('streaming_url', sa.Text(), nullable=True),
        sa.Column('video_type', sa.String(length=50), nullable=False),
        sa.Column('duration_seconds', sa.Integer(), nullable=True),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('resolution', sa.String(length=20), nullable=True),
        sa.Column('codec', sa.String(length=50), nullable=True),
        sa.Column('processing_status', sa.String(length=50), server_default='pending', nullable=True),
        sa.Column('thumbnails', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('storage_backend', sa.String(length=50), server_default='supabase', nullable=True),
        sa.Column('status', sa.String(length=50), server_default='active', nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=True),
        sa.Column('processed_at', sa.DateTime(), nullable=True),
        sa.Column('last_accessed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_videos_product', 'video_metadata', ['product_id'], unique=False)
    op.create_index('idx_videos_type', 'video_metadata', ['video_type'], unique=False)
    op.create_index('idx_videos_status', 'video_metadata', ['status'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop storage tables
    op.drop_index('idx_videos_status', table_name='video_metadata')
    op.drop_index('idx_videos_type', table_name='video_metadata')
    op.drop_index('idx_videos_product', table_name='video_metadata')
    op.drop_table('video_metadata')
    
    op.drop_index('idx_images_accessed', table_name='image_metadata')
    op.drop_index('idx_images_status', table_name='image_metadata')
    op.drop_index('idx_images_type', table_name='image_metadata')
    op.drop_index('idx_images_product', table_name='image_metadata')
    op.drop_table('image_metadata')
    
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(op.f('idx_trends_processed'), 'trend_snapshots', ['processed'], unique=False)
    op.create_index(op.f('idx_trends_captured'), 'trend_snapshots', [sa.literal_column('captured_at DESC')], unique=False)
    op.alter_column('trend_snapshots', 'geographic_data',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               type_=postgresql.JSON(astext_type=sa.Text()),
               existing_nullable=True)
    op.alter_column('trend_snapshots', 'metrics',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               type_=postgresql.JSON(astext_type=sa.Text()),
               existing_nullable=False)
    op.alter_column('research_metrics', 'metrics_data',
               existing_type=postgresql.JSONB(astext_type=sa.Text()),
               type_=postgresql.JSON(astext_type=sa.Text()),
               existing_nullable=True)
    op.create_index(op.f('idx_opportunities_status'), 'market_opportunities', ['status'], unique=False)
    op.create_index(op.f('idx_opportunities_score'), 'market_opportunities', [sa.literal_column('score DESC')], unique=False)
    op.alter_column('market_opportunities', 'reviewed_at',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=True)
    op.alter_column('market_opportunities', 'discovery_date',
               existing_type=sa.DateTime(),
               type_=postgresql.TIMESTAMP(timezone=True),
               existing_nullable=False,
               existing_server_default=sa.text('CURRENT_TIMESTAMP'))
    op.alter_column('market_opportunities', 'status',
               existing_type=sa.Enum('PENDING', 'REVIEWED', 'APPROVED', 'REJECTED', 'PROMOTED', name='opportunitystatus'),
               type_=sa.VARCHAR(length=50),
               existing_nullable=False,
               existing_server_default=sa.text("'pending'::character varying"))
    # ### end Alembic commands ###
