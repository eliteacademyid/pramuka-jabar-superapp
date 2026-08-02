"""Add performance indexes on organisasi table

Revision ID: 005_organisasi_indexes
Revises: 004_realisasi_laporan_approval_indexes
Create Date: 2026-08-01

"""
from alembic import op

revision = '005_organisasi_indexes'
down_revision = '004_realisasi_laporan_approval_indexes'
branch_labels = None
depends_on = None


def upgrade():
    # ORDER BY created_at DESC dipakai di GET /organisasi
    op.create_index('ix_organisasi_created_at', 'organisasi', ['created_at'], unique=False)
    # filter is_active dipakai di GET /organisasi?is_active=true
    op.create_index('ix_organisasi_is_active', 'organisasi', ['is_active'], unique=False)


def downgrade():
    op.drop_index('ix_organisasi_is_active', table_name='organisasi')
    op.drop_index('ix_organisasi_created_at', table_name='organisasi')
