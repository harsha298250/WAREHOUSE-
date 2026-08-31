"""add_extended_backup_record_fields

Revision ID: a1f2e3d4c5b6
Revises: 3bbcc0985a4e
Create Date: 2026-08-19 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1f2e3d4c5b6'
down_revision: Union[str, Sequence[str], None] = '3bbcc0985a4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Phase 11 extended fields to backup_records table."""
    op.add_column('backup_records', sa.Column('backup_type', sa.String(length=50), nullable=True))
    op.add_column('backup_records', sa.Column('started_at', sa.DateTime(), nullable=True))
    op.add_column('backup_records', sa.Column('completed_at', sa.DateTime(), nullable=True))
    op.add_column('backup_records', sa.Column('storage_provider', sa.String(length=50), nullable=True))
    op.add_column('backup_records', sa.Column('bucket', sa.String(length=255), nullable=True))
    op.add_column('backup_records', sa.Column('checksum_algorithm', sa.String(length=20), nullable=True))
    op.add_column('backup_records', sa.Column('verification_status', sa.String(length=50), nullable=True))
    op.add_column('backup_records', sa.Column('verification_at', sa.DateTime(), nullable=True))
    op.add_column('backup_records', sa.Column('restore_test_status', sa.String(length=50), nullable=True))
    op.add_column('backup_records', sa.Column('restore_test_at', sa.DateTime(), nullable=True))
    op.add_column('backup_records', sa.Column('retention_status', sa.String(length=50), nullable=True))
    op.add_column('backup_records', sa.Column('initiated_by', sa.String(length=100), nullable=True))
    op.add_column('backup_records', sa.Column('audit_ref', sa.String(length=255), nullable=True))


def downgrade() -> None:
    """Remove Phase 11 extended fields from backup_records table."""
    op.drop_column('backup_records', 'audit_ref')
    op.drop_column('backup_records', 'initiated_by')
    op.drop_column('backup_records', 'retention_status')
    op.drop_column('backup_records', 'restore_test_at')
    op.drop_column('backup_records', 'restore_test_status')
    op.drop_column('backup_records', 'verification_at')
    op.drop_column('backup_records', 'verification_status')
    op.drop_column('backup_records', 'checksum_algorithm')
    op.drop_column('backup_records', 'bucket')
    op.drop_column('backup_records', 'storage_provider')
    op.drop_column('backup_records', 'completed_at')
    op.drop_column('backup_records', 'started_at')
    op.drop_column('backup_records', 'backup_type')
