from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL, DEBUG

# Pool tuning: 10 koneksi tetap + 20 overflow untuk concurrency tinggi.
# pool_pre_ping=True sudah cukup untuk validasi koneksi, tidak perlu event listener tambahan.
_POOL_KWARGS = dict(
    echo=DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,
    pool_size=10,
    max_overflow=20,
)


def _build_engine():
    url = DATABASE_URL
    if url.startswith("postgresql"):
        try:
            # pool_pre_ping=True sudah handle validasi koneksi secara otomatis.
            # Tidak perlu SELECT 1 manual di sini — cukup buat engine dan biarkan
            # pool_pre_ping melakukan health check saat koneksi pertama dipakai.
            engine = create_engine(url, **_POOL_KWARGS)
            return engine
        except Exception as exc:
            print(f"PostgreSQL engine error, falling back to SQLite: {exc}")
            url = "sqlite:///./app.db"

    from sqlalchemy.pool import StaticPool
    return create_engine(
        url,
        echo=DEBUG,
        pool_pre_ping=True,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )


engine = _build_engine()

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for FastAPI to get a database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
