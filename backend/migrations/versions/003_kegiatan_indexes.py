"""Add performance indexes on kegiatans table

Revision ID: 003_kegiatan_indexes
Revises: 002_realisasi_laporan_approval
Create Date: 2026-08-01

"""
from alembic import op
import sqlalchemy as sa

revision = '003_kegiatan_indexes'
down_revision = '002_realisasi_laporan_approval'
branch_labels = None
depends_on = None


def upgrade():
    # Index single-column yang belum ada
    op.create_index('ix_kegiatans_program_id', 'kegiatans', ['program_id'], unique=False)
    op.create_index('ix_kegiatans_tanggal_mulai', 'kegiatans', ['tanggal_mulai'], unique=False)
    op.create_index('ix_kegiatans_created_at', 'kegiatans', ['created_at'], unique=False)

    # Composite index untuk filter program_id + status (pola paling umum)
    op.create_index('ix_kegiatans_program_status', 'kegiatans', ['program_id', 'status'], unique=False)


def downgrade():
    op.drop_index('ix_kegiatans_program_status', table_name='kegiatans')
    op.drop_index('ix_kegiatans_created_at', table_name='kegiatans')
    op.drop_index('ix_kegiatans_tanggal_mulai', table_name='kegiatans')
    op.drop_index('ix_kegiatans_program_id', table_name='kegiatans')
