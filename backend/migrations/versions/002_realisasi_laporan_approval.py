"""Add realisasi, dokumen, laporan, and approval tables

Revision ID: 002_realisasi_laporan_approval
Revises: 001_initial
Create Date: 2026-08-01 16:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '002_realisasi_laporan_approval'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'realisasi',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('judul', sa.String(length=200), nullable=False),
        sa.Column('deskripsi', sa.Text(), nullable=True),
        sa.Column('target', sa.Integer(), nullable=True),
        sa.Column('realisasi', sa.Integer(), nullable=True),
        sa.Column('periode', sa.String(length=50), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('file_url', sa.String(length=500), nullable=True),
        sa.Column('file_name', sa.String(length=255), nullable=True),
        sa.Column('program_id', sa.Integer(), nullable=True),
        sa.Column('kegiatan_id', sa.Integer(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['kegiatan_id'], ['kegiatans.id']),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_realisasi_judul'), 'realisasi', ['judul'])
    op.create_index(op.f('ix_realisasi_status'), 'realisasi', ['status'])

    op.create_table(
        'dokumen',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nama_file', sa.String(length=255), nullable=False),
        sa.Column('url', sa.String(length=500), nullable=False),
        sa.Column('tipe', sa.String(length=100), nullable=True),
        sa.Column('ukuran', sa.Integer(), nullable=True),
        sa.Column('realisasi_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['realisasi_id'], ['realisasi.id']),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table(
        'laporans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('judul', sa.String(length=200), nullable=False),
        sa.Column('periode', sa.String(length=50), nullable=True),
        sa.Column('deskripsi', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('realisasi_id', sa.Integer(), nullable=True),
        sa.Column('created_by_id', sa.Integer(), nullable=False),
        sa.Column('approved_by_id', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['approved_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['created_by_id'], ['users.id']),
        sa.ForeignKeyConstraint(['realisasi_id'], ['realisasi.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_laporans_judul'), 'laporans', ['judul'])
    op.create_index(op.f('ix_laporans_status'), 'laporans', ['status'])

    op.create_table(
        'approvals',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('laporan_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('catatan', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['laporan_id'], ['laporans.id']),
        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_approvals_status'), 'approvals', ['status'])


def downgrade() -> None:
    op.drop_index(op.f('ix_approvals_status'), table_name='approvals')
    op.drop_table('approvals')
    op.drop_index(op.f('ix_laporans_status'), table_name='laporans')
    op.drop_index(op.f('ix_laporans_judul'), table_name='laporans')
    op.drop_table('laporans')
    op.drop_table('dokumen')
    op.drop_index(op.f('ix_realisasi_status'), table_name='realisasi')
    op.drop_index(op.f('ix_realisasi_judul'), table_name='realisasi')
    op.drop_table('realisasi')
