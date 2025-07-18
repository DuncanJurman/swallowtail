"""Initial schema with products, agents, tasks

Revision ID: 2c2c208bb900
Revises: 
Create Date: 2025-07-13 20:52:06.054514

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2c2c208bb900'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('agents',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('type', sa.Enum('TREND_SCANNER', 'MARKET_ANALYZER', 'SOURCING_SCOUT', 'OPPORTUNITY_EVALUATOR', 'CONTENT_GENERATOR', 'MARKETING_MANAGER', 'FULFILLMENT_AGENT', 'ANALYTICS_ENGINE', 'CUSTOMER_SERVICE', name='agenttype'), nullable=False),
    sa.Column('name', sa.String(length=100), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('configuration', sa.JSON(), nullable=True),
    sa.Column('capabilities', sa.JSON(), nullable=True),
    sa.Column('total_tasks_completed', sa.Integer(), nullable=True),
    sa.Column('success_rate', sa.Float(), nullable=True),
    sa.Column('average_task_duration', sa.Float(), nullable=True),
    sa.Column('performance_metrics', sa.JSON(), nullable=True),
    sa.Column('is_active', sa.Boolean(), nullable=True),
    sa.Column('last_active_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('market_opportunities',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('discovered_by_agent_id', sa.UUID(), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('category', sa.String(length=100), nullable=True),
    sa.Column('source', sa.String(length=100), nullable=True),
    sa.Column('initial_score', sa.Float(), nullable=True),
    sa.Column('final_score', sa.Float(), nullable=True),
    sa.Column('scoring_breakdown', sa.JSON(), nullable=True),
    sa.Column('market_data', sa.JSON(), nullable=True),
    sa.Column('trend_data', sa.JSON(), nullable=True),
    sa.Column('competition_data', sa.JSON(), nullable=True),
    sa.Column('is_processed', sa.Boolean(), nullable=True),
    sa.Column('is_approved', sa.Boolean(), nullable=True),
    sa.Column('processed_at', sa.DateTime(), nullable=True),
    sa.Column('approval_notes', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['discovered_by_agent_id'], ['agents.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('products',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('status', sa.Enum('DISCOVERED', 'EVALUATING', 'APPROVED', 'REJECTED', 'SOURCING', 'LISTING', 'ACTIVE', 'PAUSED', 'DISCONTINUED', name='productstatus'), nullable=False),
    sa.Column('category', sa.String(length=100), nullable=True),
    sa.Column('tags', sa.JSON(), nullable=True),
    sa.Column('target_market', sa.JSON(), nullable=True),
    sa.Column('competition_analysis', sa.JSON(), nullable=True),
    sa.Column('cost_price', sa.Float(), nullable=True),
    sa.Column('selling_price', sa.Float(), nullable=True),
    sa.Column('profit_margin', sa.Float(), nullable=True),
    sa.Column('opportunity_score', sa.Float(), nullable=True),
    sa.Column('market_demand_score', sa.Float(), nullable=True),
    sa.Column('competition_score', sa.Float(), nullable=True),
    sa.Column('sourcing_difficulty_score', sa.Float(), nullable=True),
    sa.Column('supplier_info', sa.JSON(), nullable=True),
    sa.Column('sourcing_data', sa.JSON(), nullable=True),
    sa.Column('shopify_product_id', sa.String(length=100), nullable=True),
    sa.Column('listing_data', sa.JSON(), nullable=True),
    sa.Column('discovered_by_agent_id', sa.UUID(), nullable=True),
    sa.Column('discovered_at', sa.DateTime(), nullable=True),
    sa.Column('approved_at', sa.DateTime(), nullable=True),
    sa.Column('rejected_at', sa.DateTime(), nullable=True),
    sa.Column('rejection_reason', sa.Text(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['discovered_by_agent_id'], ['agents.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('agent_decisions',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('agent_id', sa.UUID(), nullable=False),
    sa.Column('product_id', sa.UUID(), nullable=True),
    sa.Column('decision_type', sa.String(length=50), nullable=False),
    sa.Column('decision', sa.JSON(), nullable=False),
    sa.Column('reasoning', sa.Text(), nullable=True),
    sa.Column('confidence_score', sa.Float(), nullable=True),
    sa.Column('context', sa.JSON(), nullable=True),
    sa.Column('alternatives_considered', sa.JSON(), nullable=True),
    sa.Column('requires_approval', sa.Boolean(), nullable=True),
    sa.Column('is_approved', sa.Boolean(), nullable=True),
    sa.Column('approved_by', sa.String(length=100), nullable=True),
    sa.Column('approved_at', sa.DateTime(), nullable=True),
    sa.Column('approval_notes', sa.Text(), nullable=True),
    sa.Column('outcome', sa.JSON(), nullable=True),
    sa.Column('outcome_timestamp', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('agent_tasks',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('agent_id', sa.UUID(), nullable=False),
    sa.Column('product_id', sa.UUID(), nullable=True),
    sa.Column('task_type', sa.String(length=50), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('parameters', sa.JSON(), nullable=True),
    sa.Column('status', sa.Enum('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED', name='taskstatus'), nullable=False),
    sa.Column('result', sa.JSON(), nullable=True),
    sa.Column('error_message', sa.Text(), nullable=True),
    sa.Column('retry_count', sa.Integer(), nullable=True),
    sa.Column('celery_task_id', sa.String(length=100), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('started_at', sa.DateTime(), nullable=True),
    sa.Column('completed_at', sa.DateTime(), nullable=True),
    sa.Column('duration_seconds', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['agent_id'], ['agents.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('shared_knowledge',
    sa.Column('id', sa.UUID(), nullable=False),
    sa.Column('knowledge_type', sa.String(length=50), nullable=False),
    sa.Column('category', sa.String(length=100), nullable=True),
    sa.Column('tags', sa.JSON(), nullable=True),
    sa.Column('title', sa.String(length=255), nullable=False),
    sa.Column('content', sa.Text(), nullable=True),
    sa.Column('data', sa.JSON(), nullable=True),
    sa.Column('source_agent_id', sa.UUID(), nullable=True),
    sa.Column('source_product_id', sa.UUID(), nullable=True),
    sa.Column('embedding_id', sa.String(length=100), nullable=True),
    sa.Column('usage_count', sa.Integer(), nullable=True),
    sa.Column('last_accessed_at', sa.DateTime(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['source_agent_id'], ['agents.id'], ),
    sa.ForeignKeyConstraint(['source_product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('shared_knowledge')
    op.drop_table('agent_tasks')
    op.drop_table('agent_decisions')
    op.drop_table('products')
    op.drop_table('market_opportunities')
    op.drop_table('agents')
    # ### end Alembic commands ###
