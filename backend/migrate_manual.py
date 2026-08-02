"""
Migrasi manual: buat semua index baru untuk tabel kegiatan, realisasi,
dokumen, laporans, dan approvals.

Jalankan dari folder backend/:
    python migrate_manual.py

Script ini aman dijalankan berkali-kali (IF NOT EXISTS / exception handled).
"""

import sys
import os

sys.path.insert(0, os.path.dirname(__file__))

from sqlalchemy import text
from app.database import engine


# ── Daftar index yang akan dibuat ─────────────────────────────────────────────
# Format: (index_name, table_name, columns, unique)
INDEXES = [
    # kegiatan (dari migrasi 003)
    ("ix_kegiatans_program_id",       "kegiatans",  ["program_id"],           False),
    ("ix_kegiatans_tanggal_mulai",    "kegiatans",  ["tanggal_mulai"],        False),
    ("ix_kegiatans_created_at",       "kegiatans",  ["created_at"],           False),
    ("ix_kegiatans_program_status",   "kegiatans",  ["program_id", "status"], False),

    # realisasi (dari migrasi 004)
    ("ix_realisasi_program_id",           "realisasi", ["program_id"],                False),
    ("ix_realisasi_kegiatan_id",          "realisasi", ["kegiatan_id"],               False),
    ("ix_realisasi_created_by_id",        "realisasi", ["created_by_id"],             False),
    ("ix_realisasi_created_at",           "realisasi", ["created_at"],                False),
    ("ix_realisasi_status_created",       "realisasi", ["status", "created_at"],      False),
    ("ix_realisasi_created_by_status",    "realisasi", ["created_by_id", "status"],   False),

    # dokumen
    ("ix_dokumen_realisasi_id",       "dokumen",   ["realisasi_id"],          False),

    # laporans
    ("ix_laporans_realisasi_id",      "laporans",  ["realisasi_id"],          False),
    ("ix_laporans_created_by_id",     "laporans",  ["created_by_id"],         False),
    ("ix_laporans_created_at",        "laporans",  ["created_at"],            False),
    ("ix_laporans_status_created",    "laporans",  ["status", "created_at"],  False),

    # approvals
    ("ix_approvals_laporan_id",       "approvals",   ["laporan_id"],  False),
    ("ix_approvals_user_id",          "approvals",   ["user_id"],     False),

    # organisasi (dari migrasi 005)
    ("ix_organisasi_created_at",      "organisasi",  ["created_at"],  False),
    ("ix_organisasi_is_active",       "organisasi",  ["is_active"],   False),

    # users (dari migrasi 006)
    ("ix_users_role_id",              "users",       ["role_id"],      False),
    ("ix_users_organisasi_id",        "users",       ["organisasi_id"], False),
    ("ix_users_is_active",            "users",       ["is_active"],    False),
    ("ix_users_created_at",           "users",       ["created_at"],   False),

    # programs (dari migrasi 007)
    ("ix_programs_creator_id",           "programs", ["creator_id"],             False),
    ("ix_programs_organisasi_id",        "programs", ["organisasi_id"],           False),
    ("ix_programs_created_at",           "programs", ["created_at"],             False),
    ("ix_programs_tahun_status",         "programs", ["tahun", "status"],         False),
    ("ix_programs_organisasi_status",    "programs", ["organisasi_id", "status"], False),
]


def build_create_sql(index_name, table_name, columns, unique, dialect):
    unique_kw = "UNIQUE " if unique else ""
    cols = ", ".join(columns)

    if dialect == "sqlite":
        return (
            f"CREATE {unique_kw}INDEX IF NOT EXISTS {index_name} "
            f"ON {table_name} ({cols})"
        )
    else:
        # PostgreSQL tidak support IF NOT EXISTS di CREATE INDEX sebelum PG 9.5,
        # tapi versi modern sudah support. Pakai DO block untuk aman.
        return (
            f"DO $$ BEGIN "
            f"CREATE {unique_kw}INDEX {index_name} ON {table_name} ({cols}); "
            f"EXCEPTION WHEN duplicate_table THEN NULL; "
            f"END $$"
        )


def main():
    dialect = engine.dialect.name  # 'sqlite' or 'postgresql'
    print(f"Database: {engine.url}")
    print(f"Dialect : {dialect}")
    print("-" * 60)

    created = 0
    skipped = 0

    with engine.begin() as conn:
        for index_name, table_name, columns, unique in INDEXES:
            cols_str = ", ".join(columns)

            # Cek apakah index sudah ada (SQLite)
            if dialect == "sqlite":
                exists = conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type='index' AND name=:n"),
                    {"n": index_name}
                ).fetchone()
                if exists:
                    print(f"  SKIP  {index_name} (sudah ada)")
                    skipped += 1
                    continue

                sql = f"CREATE {'UNIQUE ' if unique else ''}INDEX {index_name} ON {table_name} ({cols_str})"
                conn.execute(text(sql))
                print(f"  OK    {index_name} ON {table_name}({cols_str})")
                created += 1

            else:
                # PostgreSQL — cek pg_indexes
                exists = conn.execute(
                    text("SELECT 1 FROM pg_indexes WHERE indexname = :n"),
                    {"n": index_name}
                ).fetchone()
                if exists:
                    print(f"  SKIP  {index_name} (sudah ada)")
                    skipped += 1
                    continue

                sql = f"CREATE {'UNIQUE ' if unique else ''}INDEX {index_name} ON {table_name} ({cols_str})"
                conn.execute(text(sql))
                print(f"  OK    {index_name} ON {table_name}({cols_str})")
                created += 1

    print("-" * 60)
    print(f"Selesai: {created} index dibuat, {skipped} dilewati (sudah ada).")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\nERROR: {e}", file=sys.stderr)
        sys.exit(1)
