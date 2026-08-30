"""phase7_digital_twin_simulation

Revision ID: a1b2c3d4e5f6
Revises: eb5571a52c39
Create Date: 2026-08-18 21:43:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'eb5571a52c39'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Phase 7: Digital Twin Simulation tables."""
    # digital_twin_simulations
    op.create_table(
        'digital_twin_simulations',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('warehouse_id', sa.String(length=20), nullable=False),
        sa.Column('simulation_status', sa.String(length=20), nullable=False, server_default='IDLE'),
        sa.Column('simulation_time_seconds', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('speed_multiplier', sa.Float(), nullable=False, server_default='1.0'),
        sa.Column('seed', sa.Integer(), nullable=False, server_default='42'),
        sa.Column('mode', sa.String(length=20), nullable=False, server_default='OBSERVATION'),
        sa.Column('scenario_type', sa.String(length=30), nullable=False, server_default='NORMAL_OPERATIONS'),
        sa.Column('tick_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('started_at', sa.DateTime(), nullable=True),
        sa.Column('paused_at', sa.DateTime(), nullable=True),
        sa.Column('stopped_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_by', sa.String(length=64), nullable=False, server_default='system'),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_dts_warehouse_id', 'digital_twin_simulations', ['warehouse_id'])
    op.create_index('ix_dts_status', 'digital_twin_simulations', ['simulation_status'])
    op.create_index('ix_dts_created_at', 'digital_twin_simulations', ['created_at'])

    # simulation_snapshots
    op.create_table(
        'simulation_snapshots',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('simulation_id', sa.Integer(), nullable=False),
        sa.Column('warehouse_id', sa.String(length=20), nullable=False),
        sa.Column('snapshot_version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('taken_at', sa.DateTime(), nullable=False),
        sa.Column('sim_time_seconds', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('robot_states', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('task_states', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('obstacle_states', sa.Text(), nullable=False, server_default='[]'),
        sa.Column('sim_inventory_delta', sa.Text(), nullable=False, server_default='{}'),
        sa.Column('metadata', sa.Text(), nullable=False, server_default='{}'),
        sa.ForeignKeyConstraint(['simulation_id'], ['digital_twin_simulations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ss_simulation_id', 'simulation_snapshots', ['simulation_id'])
    op.create_index('ix_ss_warehouse_id', 'simulation_snapshots', ['warehouse_id'])

    # simulation_events
    op.create_table(
        'simulation_events',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('simulation_id', sa.Integer(), nullable=False),
        sa.Column('warehouse_id', sa.String(length=20), nullable=False),
        sa.Column('event_type', sa.String(length=50), nullable=False),
        sa.Column('severity', sa.String(length=10), nullable=False, server_default='INFO'),
        sa.Column('sim_time_seconds', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('real_timestamp', sa.DateTime(), nullable=False),
        sa.Column('robot_id', sa.Integer(), nullable=True),
        sa.Column('task_id', sa.Integer(), nullable=True),
        sa.Column('location_id', sa.String(length=50), nullable=True),
        sa.Column('route_id', sa.Integer(), nullable=True),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('metadata', sa.Text(), nullable=False, server_default='{}'),
        sa.ForeignKeyConstraint(['simulation_id'], ['digital_twin_simulations.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['warehouse_id'], ['warehouses.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_se_simulation_id', 'simulation_events', ['simulation_id'])
    op.create_index('ix_se_warehouse_id', 'simulation_events', ['warehouse_id'])
    op.create_index('ix_se_event_type', 'simulation_events', ['event_type'])
    op.create_index('ix_se_real_timestamp', 'simulation_events', ['real_timestamp'])
    op.create_index('ix_se_robot_id', 'simulation_events', ['robot_id'])
    op.create_index('ix_se_task_id', 'simulation_events', ['task_id'])


def downgrade() -> None:
    """Remove Phase 7 Digital Twin tables."""
    op.drop_table('simulation_events')
    op.drop_table('simulation_snapshots')
    op.drop_table('digital_twin_simulations')
