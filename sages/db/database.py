"""
Database session management and initialization.
Handles SQLAlchemy engine, session creation, and database initialization.
"""

import logging
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from sages.config import get_config
from sages.db.models import Base

logger = logging.getLogger(__name__)

# Global database engine and session factory
_engine = None
_SessionLocal = None


def get_engine():
    """
    Get or create the SQLAlchemy engine.

    Returns:
        SQLAlchemy engine instance
    """
    global _engine
    if _engine is None:
        # Get database URL from environment or config
        # Priority: env var > config file > default
        import os

        database_url = os.getenv("DATABASE_URL")
        if not database_url:
            config = get_config()
            database_url = config.get("database.url", "sqlite:///./data/opssage.db")

        config = get_config()
        echo = config.get("database.echo", False)

        logger.info(f"Initializing database engine with URL: {database_url.split('@')[-1]}")

        # Create engine with connection pooling for PostgreSQL
        if database_url.startswith("postgresql"):
            _engine = create_engine(
                database_url,
                echo=echo,
                pool_size=10,
                max_overflow=20,
                pool_pre_ping=True,  # Verify connections before using
            )
        else:
            # SQLite configuration
            _engine = create_engine(
                database_url,
                echo=echo,
                connect_args={"check_same_thread": False},  # Needed for SQLite
            )

    return _engine


def get_session_factory() -> sessionmaker:
    """
    Get or create the session factory.

    Returns:
        SQLAlchemy sessionmaker instance
    """
    global _SessionLocal
    if _SessionLocal is None:
        engine = get_engine()
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    return _SessionLocal


def init_db() -> None:
    """
    Initialize the database by creating all tables.
    Should be called once at application startup.
    """
    engine = get_engine()
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")


@contextmanager
def get_db() -> Generator[Session, None, None]:
    """
    Context manager for database sessions.

    Yields:
        SQLAlchemy Session instance

    Example:
        with get_db() as db:
            incident = db.query(IncidentModel).filter_by(incident_id=id).first()
    """
    SessionLocal = get_session_factory()
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


def get_db_session() -> Session:
    """
    Get a new database session.
    Caller is responsible for closing the session.

    Returns:
        SQLAlchemy Session instance

    Note:
        Prefer using the get_db() context manager for automatic cleanup.
    """
    SessionLocal = get_session_factory()
    return SessionLocal()
