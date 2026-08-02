"""Add deadline reminders feature: deadline column to laporans and new deadline_reminders table

Revision ID: 008_deadline_reminders
Revises: 007_programs_indexes
Create Date: 2026-08-02

"""
from alembic import op
import sqlalchemy as sa


revision = '008_deadline_reminders'
down_revision = '007_programs_indexes'
branch_labels = None
depends_on = None


def upgrade():
    # Tambah kolom deadline ke tabel laporans
    op.add_column('laporans', sa.Column('deadline', sa.DateTime(), nullable=True))
    op.create_index('ix_laporans_deadline', 'laporans', ['deadline'], unique=False)

    # Buat tabel deadline_reminders
    op.create_table(
        'deadline_reminders',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('laporan_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('reminder_type', sa.String(length=20), nullable=False),
        sa.Column('is_sent', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('sent_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['laporan_id'], ['laporans.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Buat indexes untuk optimal query performance
    op.create_index('ix_deadline_reminders_laporan_id', 'deadline_reminders', ['laporan_id'], unique=False)
    op.create_index('ix_deadline_reminders_user_id', 'deadline_reminders', ['user_id'], unique=False)
    op.create_index('ix_deadline_reminders_reminder_type', 'deadline_reminders', ['reminder_type'], unique=False)
    op.create_index('ix_deadline_reminders_is_sent', 'deadline_reminders', ['is_sent'], unique=False)
    op.create_index('ix_deadline_reminders_user_sent', 'deadline_reminders', ['user_id', 'is_sent'], unique=False)
    op.create_index('ix_deadline_reminders_laporan_type', 'deadline_reminders', ['laporan_id', 'reminder_type'], unique=False)


def downgrade():
    op.drop_index('ix_deadline_reminders_laporan_type', table_name='deadline_reminders')
    op.drop_index('ix_deadline_reminders_user_sent', table_name='deadline_reminders')
    op.drop_index('ix_deadline_reminders_is_sent', table_name='deadline_reminders')
    op.drop_index('ix_deadline_reminders_reminder_type', table_name='deadline_reminders')
    op.drop_index('ix_deadline_reminders_user_id', table_name='deadline_reminders')
    op.drop_index('ix_deadline_reminders_laporan_id', table_name='deadline_reminders')
    op.drop_table('deadline_reminders')
    
    op.drop_index('ix_laporans_deadline', table_name='laporans')
    op.drop_column('laporans', 'deadline')
