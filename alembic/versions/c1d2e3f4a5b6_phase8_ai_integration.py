"""phase8_ai_integration

Revision ID: c1d2e3f4a5b6
Revises: a1b2c3d4e5f6
Create Date: 2026-08-19 00:17:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c1d2e3f4a5b6'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to ai_recommendations table
    op.add_column('ai_recommendations', sa.Column('recommendation_type', sa.String(length=50), nullable=True))
    op.add_column('ai_recommendations', sa.Column('description', sa.Text(), nullable=True))
    op.add_column('ai_recommendations', sa.Column('priority', sa.String(length=20), nullable=True, server_default='MEDIUM'))
    op.add_column('ai_recommendations', sa.Column('score', sa.Integer(), nullable=True, server_default='0'))
    op.add_column('ai_recommendations', sa.Column('confidence_or_reliability', sa.String(length=50), nullable=True, server_default='HIGH'))
    op.add_column('ai_recommendations', sa.Column('source_model', sa.String(length=50), nullable=True))
    op.add_column('ai_recommendations', sa.Column('source_entity_type', sa.String(length=50), nullable=True))
    op.add_column('ai_recommendations', sa.Column('source_entity_id', sa.String(length=50), nullable=True))
    op.add_column('ai_recommendations', sa.Column('recommended_action', sa.String(length=200), nullable=True))
    op.add_column('ai_recommendations', sa.Column('estimated_impact', sa.Float(), nullable=True))
    op.add_column('ai_recommendations', sa.Column('explanation', sa.Text(), nullable=True))
    op.add_column('ai_recommendations', sa.Column('supporting_metrics', sa.Text(), nullable=True, server_default='{}'))
    op.add_column('ai_recommendations', sa.Column('created_at', sa.DateTime(), nullable=True))
    op.add_column('ai_recommendations', sa.Column('reviewed_at', sa.DateTime(), nullable=True))
    op.add_column('ai_recommendations', sa.Column('reviewed_by', sa.String(length=64), nullable=True))
    op.add_column('ai_recommendations', sa.Column('review_notes', sa.Text(), nullable=True))
    op.add_column('ai_recommendations', sa.Column('expires_at', sa.DateTime(), nullable=True))
    op.add_column('ai_recommendations', sa.Column('metadata', sa.Text(), nullable=True, server_default='{}'))

    # Populate created_at with timestamp values for existing records
    op.execute("UPDATE ai_recommendations SET created_at = timestamp WHERE created_at IS NULL")
    
    # Set default values for status to NEW for old PENDING records
    op.execute("UPDATE ai_recommendations SET status = 'NEW' WHERE status = 'PENDING'")

    # Alter created_at to non-nullable now that it is populated
    op.alter_column('ai_recommendations', 'created_at', nullable=False)
    op.alter_column('ai_recommendations', 'metadata', nullable=False)

    # Create indexes
    op.create_index('ix_air_rec_type', 'ai_recommendations', ['recommendation_type'])
    op.create_index('ix_air_created_at', 'ai_recommendations', ['created_at'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('ix_air_created_at', table_name='ai_recommendations')
    op.drop_index('ix_air_rec_type', table_name='ai_recommendations')

    # Drop columns
    op.drop_column('ai_recommendations', 'metadata')
    op.drop_column('ai_recommendations', 'expires_at')
    op.drop_column('ai_recommendations', 'review_notes')
    op.drop_column('ai_recommendations', 'reviewed_by')
    op.drop_column('ai_recommendations', 'reviewed_at')
    op.drop_column('ai_recommendations', 'created_at')
    op.drop_column('ai_recommendations', 'supporting_metrics')
    op.drop_column('ai_recommendations', 'explanation')
    op.drop_column('ai_recommendations', 'estimated_impact')
    op.drop_column('ai_recommendations', 'recommended_action')
    op.drop_column('ai_recommendations', 'source_entity_id')
    op.drop_column('ai_recommendations', 'source_entity_type')
    op.drop_column('ai_recommendations', 'source_model')
    op.drop_column('ai_recommendations', 'confidence_or_reliability')
    op.drop_column('ai_recommendations', 'score')
    op.drop_column('ai_recommendations', 'priority')
    op.drop_column('ai_recommendations', 'description')
    op.drop_column('ai_recommendations', 'recommendation_type')
