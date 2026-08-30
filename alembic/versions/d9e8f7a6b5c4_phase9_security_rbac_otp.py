"""phase9_security_rbac_otp

Revision ID: d9e8f7a6b5c4
Revises: c1d2e3f4a5b6
Create Date: 2026-08-19 01:31:00.000000

Phase 9: Security, RBAC, OTP & Enterprise Audit
- Add security fields to users table
- Create otp_records table (DB-persisted OTPs)
- Create user_sessions table (session tracking)
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd9e8f7a6b5c4'
down_revision: Union[str, Sequence[str], None] = 'c1d2e3f4a5b6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------------------------
    # 1. Extend users table with security fields
    # -------------------------------------------------------------------
    op.add_column('users', sa.Column('email', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'))
    op.add_column('users', sa.Column('is_verified', sa.Boolean(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('last_login_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('last_logout_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('last_login_ip', sa.String(length=45), nullable=True))
    op.add_column('users', sa.Column('login_location', sa.String(length=255), nullable=True))
    op.add_column('users', sa.Column('login_method', sa.String(length=30), nullable=True))
    op.add_column('users', sa.Column('failed_login_count', sa.Integer(), nullable=False, server_default='0'))
    op.add_column('users', sa.Column('locked_until', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('email_verified_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('password_changed_at', sa.DateTime(), nullable=True))
    op.add_column('users', sa.Column('updated_at', sa.DateTime(), nullable=True))

    # Backfill: existing users are active + verified (they were created before this phase)
    op.execute("UPDATE users SET is_active = TRUE, is_verified = TRUE, failed_login_count = 0")
    # For Google OAuth users, email = username (already email format)
    op.execute("UPDATE users SET email = username WHERE email IS NULL")

    # -------------------------------------------------------------------
    # 2. Create otp_records table (DB-persisted, replaces in-memory dicts)
    # -------------------------------------------------------------------
    op.create_table(
        'otp_records',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('purpose', sa.String(length=50), nullable=False),
        # ACCOUNT_ACTIVATION | EMAIL_VERIFICATION | PASSWORD_CHANGE | PASSWORD_RESET | SENSITIVE_ACTION | ADMIN_CREATION
        sa.Column('code_hash', sa.String(length=255), nullable=False),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('attempts', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('max_attempts', sa.Integer(), nullable=False, server_default='5'),
        sa.Column('consumed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('request_ip', sa.String(length=45), nullable=True),
        sa.Column('metadata', sa.Text(), nullable=True, server_default='{}'),
        # Additional context: for ADMIN_CREATION, store the target email in metadata
        sa.Column('context_data', sa.Text(), nullable=True, server_default='{}'),
    )
    op.create_index('ix_otp_user_purpose', 'otp_records', ['user_id', 'purpose'])
    op.create_index('ix_otp_expires_at', 'otp_records', ['expires_at'])

    # -------------------------------------------------------------------
    # 3. Create user_sessions table (for session lifecycle tracking)
    # -------------------------------------------------------------------
    op.create_table(
        'user_sessions',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='CASCADE'), nullable=False),
        sa.Column('session_token_hash', sa.String(length=64), nullable=False, unique=True),
        # SHA-256 of the JWT jti claim or token prefix for reference
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('last_seen_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=False),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('revoke_reason', sa.String(length=100), nullable=True),
        sa.Column('login_method', sa.String(length=30), nullable=True),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('login_location', sa.String(length=255), nullable=True),
        sa.Column('user_agent', sa.String(length=500), nullable=True),
    )
    op.create_index('ix_user_sessions_user_id', 'user_sessions', ['user_id'])
    op.create_index('ix_user_sessions_expires_at', 'user_sessions', ['expires_at'])


def downgrade() -> None:
    # Drop new tables
    op.drop_index('ix_user_sessions_expires_at', table_name='user_sessions')
    op.drop_index('ix_user_sessions_user_id', table_name='user_sessions')
    op.drop_table('user_sessions')

    op.drop_index('ix_otp_expires_at', table_name='otp_records')
    op.drop_index('ix_otp_user_purpose', table_name='otp_records')
    op.drop_table('otp_records')

    # Drop added user columns
    op.drop_column('users', 'updated_at')
    op.drop_column('users', 'password_changed_at')
    op.drop_column('users', 'email_verified_at')
    op.drop_column('users', 'locked_until')
    op.drop_column('users', 'failed_login_count')
    op.drop_column('users', 'login_method')
    op.drop_column('users', 'login_location')
    op.drop_column('users', 'last_login_ip')
    op.drop_column('users', 'last_logout_at')
    op.drop_column('users', 'last_login_at')
    op.drop_column('users', 'is_verified')
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'email')
