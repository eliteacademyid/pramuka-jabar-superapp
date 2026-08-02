"""Add performance indexes on programs table

Revision ID: 007_programs_indexes
Revises: 006_users_indexes
Create Date: 2026-08-01

"""
from alembic import op

revision = '007_programs_indexes'
down_revision = '006_users_indexes'
branch_labels = None
depends_on = None


def upgrade():
    # FK — dipakai JOIN dan filter
    op.create_index('ix_programs_creator_id',    'programs', ['creator_id'],    unique=False)
    op.create_index('ix_programs_organisasi_id', 'programs', ['organisasi_id'], unique=False)
    # ORDER BY created_at
    op.create_index('ix_programs_created_at',    'programs', ['created_at'],    unique=False)
    # Composite: filter tahun + status (pola paling umum)
    op.create_index('ix_programs_tahun_status',       'programs', ['tahun', 'status'],        unique=False)
    # Composite: filter organisasi + status
    op.create_index('ix_programs_organisasi_status',  'programs', ['organisasi_id', 'status'], unique=False)


def downgrade():
    op.drop_index('ix_programs_organisasi_status', table_name='programs')
    op.drop_index('ix_programs_tahun_status',      table_name='programs')
    op.drop_index('ix_programs_created_at',        table_name='programs')
    op.drop_index('ix_programs_organisasi_id',     table_name='programs')
    op.drop_index('ix_programs_creator_id',        table_name='programs')
