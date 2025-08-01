"""remove_unique_constraint_allow_multiple_tiktok_accounts

Revision ID: 9ed9fb38e8d5
Revises: e6494a274b11
Create Date: 2025-07-30 23:17:27.757525

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9ed9fb38e8d5'
down_revision: Union[str, Sequence[str], None] = 'e6494a274b11'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Remove unique constraint to allow multiple TikTok accounts per instance."""
    # Drop the unique constraint on instance_id
    op.drop_constraint('instance_tiktok_credentials_instance_id_key', 'instance_tiktok_credentials', type_='unique')
    
    # Add a name/alias column to distinguish multiple accounts
    op.add_column('instance_tiktok_credentials', 
        sa.Column('account_name', sa.String(length=255), nullable=True))
    
    # Create a unique constraint on (instance_id, tiktok_open_id) instead
    op.create_unique_constraint('uq_instance_tiktok_open_id', 'instance_tiktok_credentials', 
        ['instance_id', 'tiktok_open_id'])


def downgrade() -> None:
    """Revert to single TikTok account per instance."""
    # Drop the new unique constraint
    op.drop_constraint('uq_instance_tiktok_open_id', 'instance_tiktok_credentials', type_='unique')
    
    # Remove the account_name column
    op.drop_column('instance_tiktok_credentials', 'account_name')
    
    # Re-add unique constraint on instance_id
    op.create_unique_constraint('instance_tiktok_credentials_instance_id_key', 
        'instance_tiktok_credentials', ['instance_id'])
