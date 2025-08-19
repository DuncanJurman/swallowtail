"""Add instance media tables for storage tracking

Revision ID: add_instance_media
Revises: fix_timezone_tiktok
Create Date: 2025-08-17

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_instance_media'
down_revision = 'fix_timezone_tiktok'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Check if table already exists
    conn = op.get_bind()
    result = conn.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables "
        "WHERE table_name = 'instance_media')"
    ))
    table_exists = result.scalar()
    
    if table_exists:
        print("Table 'instance_media' already exists, skipping creation")
        return
    
    # Create instance_media table for tracking all media files
    op.create_table(
        'instance_media',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('instance_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('task_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('media_type', sa.String(50), nullable=False),  # 'image', 'video'
        sa.Column('media_subtype', sa.String(50), nullable=True),  # 'reference', 'generated', 'task_output', etc.
        sa.Column('storage_path', sa.Text(), nullable=False),
        sa.Column('public_url', sa.Text(), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('mime_type', sa.String(100), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['instance_id'], ['instances.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['instance_tasks.id'], ondelete='SET NULL'),
    )
    
    # Create indexes for common queries
    op.create_index('idx_instance_media_instance_id', 'instance_media', ['instance_id'])
    op.create_index('idx_instance_media_task_id', 'instance_media', ['task_id'])
    op.create_index('idx_instance_media_type', 'instance_media', ['media_type', 'media_subtype'])
    op.create_index('idx_instance_media_created_at', 'instance_media', ['created_at'])
    
    # Add unique constraint on storage_path to prevent duplicates
    op.create_unique_constraint('uq_instance_media_storage_path', 'instance_media', ['storage_path'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_instance_media_created_at', table_name='instance_media')
    op.drop_index('idx_instance_media_type', table_name='instance_media')
    op.drop_index('idx_instance_media_task_id', table_name='instance_media')
    op.drop_index('idx_instance_media_instance_id', table_name='instance_media')
    
    # Drop table
    op.drop_table('instance_media')