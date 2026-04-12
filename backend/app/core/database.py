"""Database connection and session management - Simplified SQLite Version"""
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker, Session
from app.core.config import settings


# Create sync engine for SQLite
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False},  # SQLite specific
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


def init_db():
    """Initialize database and create tables"""
    # Import all models to register them
    from app.models import user, reminder  # noqa

    # Create all tables
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created")


def get_db() -> Session:
    """Dependency for getting database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
