from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL, DEBUG

engine = create_engine(
    DATABASE_URL,
    echo=DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,
)

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
