"""phase4_task_engine

Revision ID: 451740f1aa10
Revises: ba82c39c98ef
Create Date: 2026-08-18 10:38:06.311986

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '451740f1aa10'
down_revision: Union[str, Sequence[str], None] = 'ba82c39c98ef'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Rename table picking_tasks to tasks
    op.rename_table('picking_tasks', 'tasks')

    # 2. Alter columns using batch_alter_table for SQLite/PostgreSQL compatibility
    with op.batch_alter_table('tasks') as batch_op:
        batch_op.alter_column('item_id', new_column_name='product_id', existing_type=sa.String(20))
        batch_op.alter_column('location_id', new_column_name='source_location_id', existing_type=sa.String(50))
        batch_op.alter_column('qty', new_column_name='requested_quantity', existing_type=sa.Integer())
        batch_op.alter_column('picked_qty', new_column_name='completed_quantity', existing_type=sa.Integer())

        # Add new columns as nullable first
        batch_op.add_column(sa.Column('task_number', sa.String(64), nullable=True))
        batch_op.add_column(sa.Column('warehouse_id', sa.String(20), sa.ForeignKey('warehouses.id', ondelete='CASCADE'), nullable=True))
        batch_op.add_column(sa.Column('task_type', sa.String(30), nullable=True))
        batch_op.add_column(sa.Column('priority', sa.String(20), server_default='MEDIUM', nullable=False))
        batch_op.add_column(sa.Column('priority_score', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('source_type', sa.String(30), nullable=True))
        batch_op.add_column(sa.Column('source_id', sa.String(64), nullable=True))
        batch_op.add_column(sa.Column('destination_location_id', sa.String(50), sa.ForeignKey('warehouse_locations.id', ondelete='SET NULL'), nullable=True))
        batch_op.add_column(sa.Column('assigned_user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True))
        batch_op.add_column(sa.Column('assigned_robot_id', sa.String(50), nullable=True))
        batch_op.add_column(sa.Column('prioritized_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('assigned_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('paused_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('failed_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('cancelled_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('due_at', sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column('retry_count', sa.Integer(), server_default='0', nullable=False))
        batch_op.add_column(sa.Column('failure_reason', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('metadata', sa.Text(), server_default='{}', nullable=False))
        batch_op.add_column(sa.Column('depends_on_task_id', sa.Integer(), sa.ForeignKey('tasks.id', ondelete='SET NULL'), nullable=True))

    # 3. Populate existing picking tasks data with values
    # For SQLite & Postgres, execute raw SQL updates
    op.execute("UPDATE tasks SET task_type = 'PICK' WHERE task_type IS NULL")
    op.execute("UPDATE tasks SET source_type = 'ORDER', source_id = order_id WHERE source_type IS NULL")
    
    # Update warehouse_id from orders
    op.execute(
        "UPDATE tasks SET warehouse_id = ("
        "  SELECT warehouse_id FROM orders WHERE orders.id = tasks.order_id"
        ") WHERE warehouse_id IS NULL"
    )
    # Default fallback for warehouse_id if order link fails
    op.execute("UPDATE tasks SET warehouse_id = 'WH-BLR-01' WHERE warehouse_id IS NULL")

    # Generate unique task_number
    # PostgreSQL supports lpad and concatenate; SQLite supports printf and ||
    # We will use simple concatenation that works on both or separate logic
    bind = op.get_bind()
    if bind.dialect.name == 'postgresql':
        op.execute("UPDATE tasks SET task_number = 'TSK-' || lpad(id::text, 6, '0') WHERE task_number IS NULL")
    else:
        op.execute("UPDATE tasks SET task_number = 'TSK-' || substr('000000' || id, -6) WHERE task_number IS NULL")

    # 4. Alter columns to NOT NULL and add unique constraint/indexes
    with op.batch_alter_table('tasks') as batch_op:
        batch_op.alter_column('task_number', nullable=False, existing_type=sa.String(64))
        batch_op.alter_column('warehouse_id', nullable=False, existing_type=sa.String(20))
        batch_op.alter_column('task_type', nullable=False, existing_type=sa.String(30))
        batch_op.create_unique_constraint('uq_tasks_task_number', ['task_number'])
        
        # Add indexes
        batch_op.create_index('ix_tasks_warehouse_id', ['warehouse_id'])
        batch_op.create_index('ix_tasks_status', ['status'])
        batch_op.create_index('ix_tasks_task_type', ['task_type'])
        batch_op.create_index('ix_tasks_priority_score', ['priority_score'])
        batch_op.create_index('ix_tasks_due_at', ['due_at'])
        batch_op.create_index('ix_tasks_assigned_user_id', ['assigned_user_id'])
        batch_op.create_index('ix_tasks_order_id', ['order_id'])
        batch_op.create_index('ix_tasks_product_id', ['product_id'])
        batch_op.create_index('ix_tasks_created_at', ['created_at'])

    # 5. Create task_events table
    op.create_table(
        'task_events',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('task_id', sa.Integer(), sa.ForeignKey('tasks.id', ondelete='CASCADE'), nullable=False),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('previous_status', sa.String(30), nullable=True),
        sa.Column('new_status', sa.String(30), nullable=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('metadata', sa.Text(), server_default='{}', nullable=False)
    )
    with op.batch_alter_table('task_events') as batch_op:
        batch_op.create_index('ix_task_events_task_id', ['task_id'])


def downgrade() -> None:
    # 1. Drop task_events
    op.drop_table('task_events')

    # 2. Revert tasks table changes
    with op.batch_alter_table('tasks') as batch_op:
        batch_op.drop_constraint('uq_tasks_task_number', type_='unique')
        batch_op.drop_index('ix_tasks_warehouse_id')
        batch_op.drop_index('ix_tasks_status')
        batch_op.drop_index('ix_tasks_task_type')
        batch_op.drop_index('ix_tasks_priority_score')
        batch_op.drop_index('ix_tasks_due_at')
        batch_op.drop_index('ix_tasks_assigned_user_id')
        batch_op.drop_index('ix_tasks_order_id')
        batch_op.drop_index('ix_tasks_product_id')
        batch_op.drop_index('ix_tasks_created_at')

        batch_op.drop_column('task_number')
        batch_op.drop_column('warehouse_id')
        batch_op.drop_column('task_type')
        batch_op.drop_column('priority')
        batch_op.drop_column('priority_score')
        batch_op.drop_column('source_type')
        batch_op.drop_column('source_id')
        batch_op.drop_column('destination_location_id')
        batch_op.drop_column('assigned_user_id')
        batch_op.drop_column('assigned_robot_id')
        batch_op.drop_column('prioritized_at')
        batch_op.drop_column('assigned_at')
        batch_op.drop_column('paused_at')
        batch_op.drop_column('failed_at')
        batch_op.drop_column('cancelled_at')
        batch_op.drop_column('due_at')
        batch_op.drop_column('retry_count')
        batch_op.drop_column('failure_reason')
        batch_op.drop_column('metadata')
        batch_op.drop_column('depends_on_task_id')

        # Rename back to old columns
        batch_op.alter_column('product_id', new_column_name='item_id', existing_type=sa.String(20))
        batch_op.alter_column('source_location_id', new_column_name='location_id', existing_type=sa.String(50))
        batch_op.alter_column('requested_quantity', new_column_name='qty', existing_type=sa.Integer())
        batch_op.alter_column('completed_quantity', new_column_name='picked_qty', existing_type=sa.Integer())

    # 3. Rename tasks back to picking_tasks
    op.rename_table('tasks', 'picking_tasks')
