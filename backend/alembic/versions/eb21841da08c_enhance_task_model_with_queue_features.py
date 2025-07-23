"""enhance_task_model_with_queue_features

Revision ID: eb21841da08c
Revises: 1acf3a824452
Create Date: 2025-07-23 05:58:27.618117

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'eb21841da08c'
down_revision: Union[str, None] = '1acf3a824452'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create new enums
    op.execute("CREATE TYPE taskpriority AS ENUM ('urgent', 'normal', 'low')")
    
    # Add new status values to existing enum
    op.execute("ALTER TYPE instancetaskstatus ADD VALUE IF NOT EXISTS 'submitted'")
    op.execute("ALTER TYPE instancetaskstatus ADD VALUE IF NOT EXISTS 'assigned'")
    op.execute("ALTER TYPE instancetaskstatus ADD VALUE IF NOT EXISTS 'review'")
    op.execute("ALTER TYPE instancetaskstatus ADD VALUE IF NOT EXISTS 'cancelled'")
    op.execute("ALTER TYPE instancetaskstatus ADD VALUE IF NOT EXISTS 'rejected'")
    
    # Add new columns to instance_tasks
    op.add_column('instance_tasks', 
        sa.Column('priority', sa.Enum('urgent', 'normal', 'low', name='taskpriority'), 
                  nullable=False, server_default='normal'))
    op.add_column('instance_tasks', 
        sa.Column('scheduled_for', sa.DateTime(), nullable=True))
    op.add_column('instance_tasks', 
        sa.Column('recurring_pattern', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('instance_tasks', 
        sa.Column('parsed_intent', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('instance_tasks', 
        sa.Column('execution_steps', postgresql.JSONB(astext_type=sa.Text()), 
                  nullable=False, server_default='[]'))
    op.add_column('instance_tasks', 
        sa.Column('progress_percentage', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('instance_tasks', 
        sa.Column('output_format', sa.String(length=50), nullable=True))
    op.add_column('instance_tasks', 
        sa.Column('output_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True))
    op.add_column('instance_tasks', 
        sa.Column('output_media_ids', postgresql.JSONB(astext_type=sa.Text()), 
                  nullable=False, server_default='[]'))
    op.add_column('instance_tasks', 
        sa.Column('processing_started_at', sa.DateTime(), nullable=True))
    op.add_column('instance_tasks', 
        sa.Column('processing_ended_at', sa.DateTime(), nullable=True))
    op.add_column('instance_tasks', 
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('instance_tasks', 
        sa.Column('parent_task_id', sa.UUID(), nullable=True))
    op.add_column('instance_tasks', 
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()))
    
    # Create new indexes
    op.create_index('idx_instance_tasks_priority', 'instance_tasks', 
                    ['instance_id', 'priority', 'created_at'], unique=False)
    op.create_index('idx_instance_tasks_scheduled', 'instance_tasks', 
                    ['scheduled_for', 'status'], unique=False)
    
    # Note: Default status change will be handled in a separate migration due to PostgreSQL constraints
    
    # Remove server defaults after migration
    op.alter_column('instance_tasks', 'priority', server_default=None)
    op.alter_column('instance_tasks', 'execution_steps', server_default=None)
    op.alter_column('instance_tasks', 'progress_percentage', server_default=None)
    op.alter_column('instance_tasks', 'output_media_ids', server_default=None)
    op.alter_column('instance_tasks', 'retry_count', server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    # Remove new indexes
    op.drop_index('idx_instance_tasks_scheduled', table_name='instance_tasks')
    op.drop_index('idx_instance_tasks_priority', table_name='instance_tasks')
    
    # Remove new columns
    op.drop_column('instance_tasks', 'updated_at')
    op.drop_column('instance_tasks', 'parent_task_id')
    op.drop_column('instance_tasks', 'retry_count')
    op.drop_column('instance_tasks', 'processing_ended_at')
    op.drop_column('instance_tasks', 'processing_started_at')
    op.drop_column('instance_tasks', 'output_media_ids')
    op.drop_column('instance_tasks', 'output_data')
    op.drop_column('instance_tasks', 'output_format')
    op.drop_column('instance_tasks', 'progress_percentage')
    op.drop_column('instance_tasks', 'execution_steps')
    op.drop_column('instance_tasks', 'parsed_intent')
    op.drop_column('instance_tasks', 'recurring_pattern')
    op.drop_column('instance_tasks', 'scheduled_for')
    op.drop_column('instance_tasks', 'priority')
    
    # Note: We cannot remove enum values in PostgreSQL, so the new status values will remain
    
    # Drop priority enum
    op.execute("DROP TYPE taskpriority")