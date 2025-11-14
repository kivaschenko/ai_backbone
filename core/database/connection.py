"""
Database connection and session management.
"""

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
import logging
from typing import Optional

logger = logging.getLogger(__name__)

Base = declarative_base()


class DatabaseManager:
    """Manages database connections and sessions."""

    def __init__(self, database_url: str, echo: bool = False):
        """
        Initialize database manager.

        Args:
            database_url: SQLAlchemy database URL
            echo: Whether to log SQL statements
        """
        self.engine = create_engine(database_url, echo=echo, pool_pre_ping=True)
        self.SessionLocal = scoped_session(
            sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        )

    def create_tables(self):
        """Create all tables in the database."""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")

    def drop_tables(self):
        """Drop all tables in the database."""
        Base.metadata.drop_all(bind=self.engine)
        logger.info("Database tables dropped")

    def get_session(self):
        """Get a new database session."""
        return self.SessionLocal()

    def close_session(self):
        """Close the current scoped session."""
        self.SessionLocal.remove()


# Global database manager instance
db_manager: Optional[DatabaseManager] = None


def init_db(database_url: str, echo: bool = False) -> DatabaseManager:
    """
    Initialize the global database manager.

    Args:
        database_url: SQLAlchemy database URL
        echo: Whether to log SQL statements

    Returns:
        DatabaseManager instance
    """
    global db_manager
    db_manager = DatabaseManager(database_url, echo)
    return db_manager


def get_db():
    """
    Dependency function for getting database sessions.
    Yields a session and ensures it's closed after use.
    """
    if db_manager is None:
        raise RuntimeError("Database not initialized. Call init_db() first.")

    session = db_manager.get_session()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
