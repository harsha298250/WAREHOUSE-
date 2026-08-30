"""Phase 9 — ML Analytics Tables: ForecastRun, ForecastResult, ABCClassification, AnomalyResult, ReplenishmentRecommendation

Revision ID: f1a2b3c4d5e6
Revises: c1d2e3f4a5b6
Create Date: 2026-08-21
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = 'f1a2b3c4d5e6'
down_revision = '4252c662336c'
branch_labels = None
depends_on = None


def upgrade():
    # forecast_runs
    op.create_table(
        'forecast_runs',
        sa.Column('run_id', sa.String(36), primary_key=True),
        sa.Column('dataset_id', sa.String(50), nullable=False),
        sa.Column('model_name', sa.String(100), nullable=False),
        sa.Column('grain', sa.String(100), nullable=False),
        sa.Column('train_start', sa.String(20), nullable=True),
        sa.Column('train_end', sa.String(20), nullable=True),
        sa.Column('val_start', sa.String(20), nullable=True),
        sa.Column('val_end', sa.String(20), nullable=True),
        sa.Column('horizon_days', sa.Integer, nullable=False, server_default='28'),
        sa.Column('feature_set', sa.JSON, nullable=True),
        sa.Column('params', sa.JSON, nullable=True),
        sa.Column('mae', sa.Float, nullable=True),
        sa.Column('rmse', sa.Float, nullable=True),
        sa.Column('wape_pct', sa.Float, nullable=True),
        sa.Column('smape_pct', sa.Float, nullable=True),
        sa.Column('naive_wape_pct', sa.Float, nullable=True),
        sa.Column('ma_wape_pct', sa.Float, nullable=True),
        sa.Column('wape_improvement_pct', sa.Float, nullable=True),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    op.create_index('ix_forecast_runs_dataset_id', 'forecast_runs', ['dataset_id'])

    # forecast_results
    op.create_table(
        'forecast_results',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('run_id', sa.String(36), sa.ForeignKey('forecast_runs.run_id', ondelete='CASCADE'), nullable=False),
        sa.Column('entity', sa.String(100), nullable=False),
        sa.Column('forecast_date', sa.String(20), nullable=False),
        sa.Column('predicted_demand', sa.Float, nullable=False),
        sa.Column('lower_bound', sa.Float, nullable=True),
        sa.Column('upper_bound', sa.Float, nullable=True),
    )
    op.create_index('ix_forecast_results_run_id', 'forecast_results', ['run_id'])
    op.create_index('ix_forecast_results_entity', 'forecast_results', ['entity'])
    op.create_index('ix_forecast_results_entity_date', 'forecast_results', ['entity', 'forecast_date'])

    # abc_classifications
    op.create_table(
        'abc_classifications',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('source', sa.String(50), nullable=False),
        sa.Column('run_at', sa.DateTime, nullable=False),
        sa.Column('item_id', sa.String(100), nullable=False),
        sa.Column('item_name', sa.String(255), nullable=True),
        sa.Column('total_qty', sa.Float, nullable=False, server_default='0.0'),
        sa.Column('total_value', sa.Float, nullable=False, server_default='0.0'),
        sa.Column('pct_contribution', sa.Float, nullable=False, server_default='0.0'),
        sa.Column('cumulative_pct', sa.Float, nullable=False, server_default='0.0'),
        sa.Column('abc_class', sa.String(1), nullable=False),
        sa.Column('threshold_a', sa.Float, nullable=False, server_default='80.0'),
        sa.Column('threshold_b', sa.Float, nullable=False, server_default='95.0'),
    )
    op.create_index('ix_abc_classifications_source', 'abc_classifications', ['source'])
    op.create_index('ix_abc_classifications_run_at', 'abc_classifications', ['run_at'])

    # anomaly_results
    op.create_table(
        'anomaly_results',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('dataset_id', sa.String(50), nullable=False),
        sa.Column('entity', sa.String(100), nullable=False),
        sa.Column('date', sa.String(20), nullable=False),
        sa.Column('anomaly_score', sa.Integer, nullable=False),
        sa.Column('is_anomaly', sa.Boolean, nullable=False, server_default='true'),
        sa.Column('severity', sa.String(10), nullable=False),
        sa.Column('reason', sa.String(255), nullable=True),
        sa.Column('features_json', sa.JSON, nullable=True),
        sa.Column('model_name', sa.String(50), nullable=False, server_default='IsolationForest'),
        sa.Column('model_version', sa.String(20), nullable=False, server_default='1.0'),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    op.create_index('ix_anomaly_results_dataset_id', 'anomaly_results', ['dataset_id'])
    op.create_index('ix_anomaly_results_date', 'anomaly_results', ['date'])
    op.create_index('ix_anomaly_results_created_at', 'anomaly_results', ['created_at'])

    # replenishment_recommendations
    op.create_table(
        'replenishment_recommendations',
        sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
        sa.Column('item_id', sa.String(100), nullable=False),
        sa.Column('item_name', sa.String(255), nullable=True),
        sa.Column('warehouse_id', sa.String(100), nullable=True),
        sa.Column('current_stock', sa.Float, nullable=True),
        sa.Column('forecast_demand', sa.Float, nullable=True),
        sa.Column('lead_time_days', sa.Integer, nullable=True),
        sa.Column('safety_stock', sa.Float, nullable=True),
        sa.Column('reorder_point', sa.Float, nullable=True),
        sa.Column('recommended_qty', sa.Float, nullable=True),
        sa.Column('abc_class', sa.String(1), nullable=True),
        sa.Column('urgency', sa.String(20), nullable=False, server_default='NO_ACTION'),
        sa.Column('status', sa.String(30), nullable=False, server_default='NO_ACTION'),
        sa.Column('reason', sa.Text, nullable=True),
        sa.Column('data_quality', sa.String(50), nullable=False, server_default='COMPLETE'),
        sa.Column('created_at', sa.DateTime, nullable=False),
    )
    op.create_index('ix_replenishment_item_id', 'replenishment_recommendations', ['item_id'])
    op.create_index('ix_replenishment_warehouse_id', 'replenishment_recommendations', ['warehouse_id'])
    op.create_index('ix_replenishment_urgency', 'replenishment_recommendations', ['urgency'])
    op.create_index('ix_replenishment_created_at', 'replenishment_recommendations', ['created_at'])


def downgrade():
    op.drop_table('replenishment_recommendations')
    op.drop_table('anomaly_results')
    op.drop_table('abc_classifications')
    op.drop_table('forecast_results')
    op.drop_table('forecast_runs')
