"""add_user_table_and_instance_fk

Revision ID: 18815335c350
Revises: 9ed9fb38e8d5
Create Date: 2025-08-04 23:20:13.155667

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '18815335c350'
down_revision: Union[str, Sequence[str], None] = '9ed9fb38e8d5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    
    # Create a default user for existing instances
    op.execute("""
        INSERT INTO users (id, email, name, is_active, created_at, updated_at)
        VALUES ('00000000-0000-0000-0000-000000000001', 'default@example.com', 'Default User', true, NOW(), NOW())
        ON CONFLICT (id) DO NOTHING
    """)
    
    # Add foreign key constraint to instances table
    op.create_foreign_key('fk_instances_user_id', 'instances', 'users', ['user_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    # Drop foreign key constraint
    op.drop_constraint('fk_instances_user_id', 'instances', type_='foreignkey')
    
    # Drop users table
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')