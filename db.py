from sqlmodel import SQLModel, create_engine, Session

from config import settings

# Create SQLite engine
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False},  # Only needed for SQLite
)


def create_db_and_tables():
    """Create database tables if they don't exist"""
    SQLModel.metadata.create_all(engine)


def get_session():
    """Dependency for database session"""
    with Session(engine) as session:
        yield session

