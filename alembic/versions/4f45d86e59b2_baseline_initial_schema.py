"""baseline_initial_schema

Revision ID: 4f45d86e59b2
Revises: None
Create Date: 2026-08-14 10:14:09.831853

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4f45d86e59b2'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Baseline tables initialization."""
    op.create_table('access_log',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('warehouse_id', sa.String(length=20), nullable=True),
    sa.Column('action', sa.String(length=50), nullable=False),
    sa.Column('ip_address', sa.String(length=45), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_access_log_timestamp'), 'access_log', ['timestamp'], unique=False)
    op.create_table('ai_recommendations',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('warehouse_id', sa.String(length=20), nullable=False),
    sa.Column('item_id', sa.String(length=50), nullable=True),
    sa.Column('title', sa.String(length=100), nullable=False),
    sa.Column('risk_level', sa.String(length=20), nullable=True),
    sa.Column('action_recommended', sa.String(length=100), nullable=False),
    sa.Column('confidence_score', sa.Integer(), nullable=True),
    sa.Column('input_factors', sa.Text(), nullable=True),
    sa.Column('status', sa.String(length=20), nullable=True),
    sa.Column('decision_by', sa.String(length=64), nullable=True),
    sa.Column('decision_time', sa.DateTime(), nullable=True),
    sa.Column('notes', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ai_recommendations_timestamp'), 'ai_recommendations', ['timestamp'], unique=False)
    op.create_table('audit_ledger',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('event_type', sa.String(length=50), nullable=False),
    sa.Column('details', sa.Text(), nullable=True),
    sa.Column('prev_hash', sa.String(length=64), nullable=False),
    sa.Column('hash', sa.String(length=64), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('items',
    sa.Column('id', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=150), nullable=False),
    sa.Column('category', sa.String(length=80), nullable=True),
    sa.Column('unit_cost', sa.Float(), nullable=True),
    sa.Column('lead_time_days', sa.Integer(), nullable=True),
    sa.Column('safety_stock', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('shrinkage_flags',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('warehouse_id', sa.String(length=20), nullable=False),
    sa.Column('item_id', sa.String(length=20), nullable=False),
    sa.Column('item_name', sa.String(length=150), nullable=True),
    sa.Column('deviation_score', sa.Float(), nullable=True),
    sa.Column('expected_quantity', sa.Float(), nullable=True),
    sa.Column('actual_quantity', sa.Float(), nullable=True),
    sa.Column('discrepancy_quantity', sa.Float(), nullable=True),
    sa.Column('estimated_exposure', sa.Float(), nullable=True),
    sa.Column('severity', sa.String(length=20), nullable=True),
    sa.Column('likely_cause', sa.String(length=80), nullable=True),
    sa.Column('explanation', sa.Text(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('username', sa.String(length=64), nullable=False),
    sa.Column('password_hash', sa.String(length=255), nullable=False),
    sa.Column('role', sa.String(length=20), nullable=False),
    sa.Column('full_name', sa.String(length=120), nullable=True),
    sa.Column('google_subject_id', sa.String(length=128), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_google_subject_id'), 'users', ['google_subject_id'], unique=False)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_table('warehouses',
    sa.Column('id', sa.String(length=20), nullable=False),
    sa.Column('name', sa.String(length=120), nullable=False),
    sa.Column('location', sa.String(length=120), nullable=True),
    sa.Column('latitude', sa.Float(), nullable=True),
    sa.Column('longitude', sa.Float(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('stock_movements',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('date', sa.Date(), nullable=False),
    sa.Column('warehouse_id', sa.String(length=20), nullable=False),
    sa.Column('item_id', sa.String(length=20), nullable=False),
    sa.Column('stock_in', sa.Integer(), nullable=True),
    sa.Column('stock_out', sa.Integer(), nullable=True),
    sa.Column('closing_stock', sa.Integer(), nullable=True),
    sa.Column('is_anomaly', sa.Boolean(), nullable=True),
    sa.Column('anomaly_type', sa.String(length=30), nullable=True),
    sa.Column('entry_source', sa.String(length=20), nullable=True),
    sa.Column('entered_by', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['items.id'], ),
    sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('date', 'warehouse_id', 'item_id', name='uq_movement')
    )
    op.create_index(op.f('ix_stock_movements_date'), 'stock_movements', ['date'], unique=False)
    op.create_index(op.f('ix_stock_movements_item_id'), 'stock_movements', ['item_id'], unique=False)
    op.create_index(op.f('ix_stock_movements_warehouse_id'), 'stock_movements', ['warehouse_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_stock_movements_warehouse_id'), table_name='stock_movements')
    op.drop_index(op.f('ix_stock_movements_item_id'), table_name='stock_movements')
    op.drop_index(op.f('ix_stock_movements_date'), table_name='stock_movements')
    op.drop_table('stock_movements')
    op.drop_table('warehouses')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_google_subject_id'), table_name='users')
    op.drop_table('users')
    op.drop_table('shrinkage_flags')
    op.drop_table('items')
    op.drop_table('audit_ledger')
    op.drop_index(op.f('ix_ai_recommendations_timestamp'), table_name='ai_recommendations')
    op.drop_table('ai_recommendations')
    op.drop_index(op.f('ix_access_log_timestamp'), table_name='access_log')
    op.drop_table('access_log')
