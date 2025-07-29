"""Add product_tasks table for task management

Revision ID: 76288c6b0a63
Revises: 240c065528c1
Create Date: 2025-07-17 23:49:06.848204

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '76288c6b0a63'
down_revision: Union[str, Sequence[str], None] = '240c065528c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Use existing taskstatus enum - no need to create it
    
    # Create product_tasks table
    op.create_table('product_tasks',
        sa.Column('id', sa.UUID(), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('product_id', sa.UUID(), nullable=False),
        sa.Column('task_description', sa.Text(), nullable=False),
        sa.Column('status', postgresql.ENUM('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED', name='taskstatus', create_type=False), nullable=False, server_default='PENDING'),
        sa.Column('priority', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('assigned_agent', sa.String(100), nullable=True),
        sa.Column('result_data', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('CURRENT_TIMESTAMP')),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_by', sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(['product_id'], ['products.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for better query performance
    op.create_index(op.f('idx_product_tasks_product_id'), 'product_tasks', ['product_id'], unique=False)
    op.create_index(op.f('idx_product_tasks_status'), 'product_tasks', ['status'], unique=False)
    op.create_index(op.f('idx_product_tasks_created_at'), 'product_tasks', ['created_at'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Drop indexes
    op.drop_index(op.f('idx_product_tasks_created_at'), table_name='product_tasks')
    op.drop_index(op.f('idx_product_tasks_status'), table_name='product_tasks')
    op.drop_index(op.f('idx_product_tasks_product_id'), table_name='product_tasks')
    
    # Drop table
    op.drop_table('product_tasks')
    
    # Don't drop the enum as it's used by other tables
