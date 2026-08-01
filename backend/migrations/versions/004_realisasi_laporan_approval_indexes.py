"""Add performance indexes on realisasi, dokumen, laporan, approval tables

Revision ID: 004_realisasi_laporan_approval_indexes
Revises: 003_kegiatan_indexes
Create Date: 2026-08-01

"""
from alembic import op

revision = '004_realisasi_laporan_approval_indexes'
down_revision = '003_kegiatan_indexes'
branch_labels = None
depends_on = None


def upgrade():
    # ── realisasi ──────────────────────────────────────────────
    op.create_index('ix_realisasi_program_id',    'realisasi', ['program_id'],    unique=False)
    op.create_index('ix_realisasi_kegiatan_id',   'realisasi', ['kegiatan_id'],   unique=False)
    op.create_index('ix_realisasi_created_by_id', 'realisasi', ['created_by_id'], unique=False)
    op.create_index('ix_realisasi_created_at',    'realisasi', ['created_at'],    unique=False)
    # Composite: filter status + order created_at
    op.create_index('ix_realisasi_status_created',    'realisasi', ['status', 'created_at'],  unique=False)
    # Composite: filter by user + status (my realisasi)
    op.create_index('ix_realisasi_created_by_status', 'realisasi', ['created_by_id', 'status'], unique=False)

    # ── dokumen ────────────────────────────────────────────────
    # selectinload Dokumen by realisasi_id pakai index ini
    op.create_index('ix_dokumen_realisasi_id', 'dokumen', ['realisasi_id'], unique=False)

    # ── laporans ───────────────────────────────────────────────
    op.create_index('ix_laporans_realisasi_id',   'laporans', ['realisasi_id'],   unique=False)
    op.create_index('ix_laporans_created_by_id',  'laporans', ['created_by_id'],  unique=False)
    op.create_index('ix_laporans_created_at',     'laporans', ['created_at'],     unique=False)
    # Composite: filter status + order created_at (pola GET /laporan)
    op.create_index('ix_laporans_status_created', 'laporans', ['status', 'created_at'], unique=False)

    # ── approvals ──────────────────────────────────────────────
    op.create_index('ix_approvals_laporan_id', 'approvals', ['laporan_id'], unique=False)
    op.create_index('ix_approvals_user_id',    'approvals', ['user_id'],    unique=False)


def downgrade():
    op.drop_index('ix_approvals_user_id',            table_name='approvals')
    op.drop_index('ix_approvals_laporan_id',         table_name='approvals')
    op.drop_index('ix_laporans_status_created',      table_name='laporans')
    op.drop_index('ix_laporans_created_at',          table_name='laporans')
    op.drop_index('ix_laporans_created_by_id',       table_name='laporans')
    op.drop_index('ix_laporans_realisasi_id',        table_name='laporans')
    op.drop_index('ix_dokumen_realisasi_id',         table_name='dokumen')
    op.drop_index('ix_realisasi_created_by_status',  table_name='realisasi')
    op.drop_index('ix_realisasi_status_created',     table_name='realisasi')
    op.drop_index('ix_realisasi_created_at',         table_name='realisasi')
    op.drop_index('ix_realisasi_created_by_id',      table_name='realisasi')
    op.drop_index('ix_realisasi_kegiatan_id',        table_name='realisasi')
    op.drop_index('ix_realisasi_program_id',         table_name='realisasi')
