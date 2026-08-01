from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL, settings

# Create engine with proper configuration
engine = create_engine(
    DATABASE_URL,
    echo=settings.DEBUG,  # Log all SQL statements in debug mode
    pool_size=10,  # Number of connections to maintain in the pool
    max_overflow=20,  # Maximum connections to create beyond pool_size
    pool_pre_ping=True,  # Test connection before using (detects dead connections)
    pool_recycle=3600,  # Recycle connections after 1 hour
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    """Dependency for FastAPI to get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Event listener to test database connection on startup
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Test connection when engine connects"""
    cursor = dbapi_conn.cursor()
    cursor.execute("SELECT 1")
    cursor.close()

