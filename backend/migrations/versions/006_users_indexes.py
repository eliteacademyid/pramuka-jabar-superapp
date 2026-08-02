"""Add performance indexes on users table

Revision ID: 006_users_indexes
Revises: 005_organisasi_indexes
Create Date: 2026-08-01

"""
from alembic import op

revision = '006_users_indexes'
down_revision = '005_organisasi_indexes'
branch_labels = None
depends_on = None


def upgrade():
    # FK role_id — dipakai joinedload dan filter by role
    op.create_index('ix_users_role_id', 'users', ['role_id'], unique=False)
    # FK organisasi_id — dipakai filter by organisasi
    op.create_index('ix_users_organisasi_id', 'users', ['organisasi_id'], unique=False)
    # filter is_active — GET /admin/users?is_active=true
    op.create_index('ix_users_is_active', 'users', ['is_active'], unique=False)
    # ORDER BY id sudah pakai PK, created_at untuk sort alternatif
    op.create_index('ix_users_created_at', 'users', ['created_at'], unique=False)


def downgrade():
    op.drop_index('ix_users_created_at',     table_name='users')
    op.drop_index('ix_users_is_active',      table_name='users')
    op.drop_index('ix_users_organisasi_id',  table_name='users')
    op.drop_index('ix_users_role_id',        table_name='users')
