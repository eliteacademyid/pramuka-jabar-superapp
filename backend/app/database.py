from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL, DEBUG


def _build_engine():
    url = DATABASE_URL
    if url.startswith("postgresql"):
        try:
            engine = create_engine(url, echo=DEBUG, pool_pre_ping=True, pool_recycle=3600)
            with engine.connect() as conn:
                conn.execute(text("SELECT 1"))
            return engine
        except OperationalError as exc:
            print(f"PostgreSQL unavailable at {url}; falling back to sqlite:///./app.db. Error: {exc}")
            url = "sqlite:///./app.db"

    return create_engine(url, echo=DEBUG, pool_pre_ping=True, pool_recycle=3600)


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


@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Verify a connection is usable when SQLAlchemy opens it."""
    cursor = dbapi_conn.cursor()
    cursor.execute("SELECT 1")
    cursor.close()
