"""Synchronous database configuration for non-async operations."""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from src.core.config import get_settings
from src.core.database import Base

settings = get_settings()

# Create sync engine  
SYNC_DATABASE_URL = settings.database_url

engine = create_engine(
    SYNC_DATABASE_URL,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
)

# Create sync session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)


def get_db() -> Generator[Session, None, None]:
    """Dependency to get sync database session."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()