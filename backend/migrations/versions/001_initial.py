"""Initial migration: Create User, Role, Organisasi, Program, Kegiatan tables

Revision ID: 001_initial
Revises: 
Create Date: 2026-08-01 16:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create Role table first
    op.create_table(
        'roles',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('description', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name')
    )
    op.create_index(op.f('ix_roles_name'), 'roles', ['name'], unique=True)

    # Create Organisasi table
    op.create_table(
        'organisasi',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nama', sa.String(length=150), nullable=False),
        sa.Column('alamat', sa.String(length=255), nullable=True),
        sa.Column('telepon', sa.String(length=20), nullable=True),
        sa.Column('email', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('nama')
    )
    op.create_index(op.f('ix_organisasi_nama'), 'organisasi', ['nama'], unique=True)

    # Create User table with foreign keys
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=False),
        sa.Column('email', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(), nullable=False),
        sa.Column('nama_lengkap', sa.String(length=100), nullable=False),
        sa.Column('role_id', sa.Integer(), nullable=False),
        sa.Column('organisasi_id', sa.Integer(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['organisasi_id'], ['organisasi.id'], ),
        sa.ForeignKeyConstraint(['role_id'], ['roles.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create Program table
    op.create_table(
        'programs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nama', sa.String(length=150), nullable=False),
        sa.Column('deskripsi', sa.String(), nullable=True),
        sa.Column('tahun', sa.Integer(), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('creator_id', sa.Integer(), nullable=False),
        sa.Column('organisasi_id', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['creator_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['organisasi_id'], ['organisasi.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_programs_nama'), 'programs', ['nama'])
    op.create_index(op.f('ix_programs_status'), 'programs', ['status'])
    op.create_index(op.f('ix_programs_tahun'), 'programs', ['tahun'])

    # Create Kegiatan table
    op.create_table(
        'kegiatans',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nama', sa.String(length=150), nullable=False),
        sa.Column('deskripsi', sa.String(), nullable=True),
        sa.Column('program_id', sa.Integer(), nullable=False),
        sa.Column('tanggal_mulai', sa.DateTime(), nullable=False),
        sa.Column('tanggal_selesai', sa.DateTime(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('lokasi', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['program_id'], ['programs.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_kegiatans_nama'), 'kegiatans', ['nama'])
    op.create_index(op.f('ix_kegiatans_status'), 'kegiatans', ['status'])


def downgrade() -> None:
    # Drop tables in reverse order of creation
    op.drop_index(op.f('ix_kegiatans_status'), table_name='kegiatans')
    op.drop_index(op.f('ix_kegiatans_nama'), table_name='kegiatans')
    op.drop_table('kegiatans')
    op.drop_index(op.f('ix_programs_tahun'), table_name='programs')
    op.drop_index(op.f('ix_programs_status'), table_name='programs')
    op.drop_index(op.f('ix_programs_nama'), table_name='programs')
    op.drop_table('programs')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    op.drop_index(op.f('ix_organisasi_nama'), table_name='organisasi')
    op.drop_table('organisasi')
    op.drop_index(op.f('ix_roles_name'), table_name='roles')
    op.drop_table('roles')
