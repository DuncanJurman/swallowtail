"""Database configuration and connection management."""

import os
import ssl
import logging
from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from src.core.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# Always use transaction pooler for application connections
# Direct connections don't work on Railway due to IPv6
if not settings.database_url:
    raise ValueError("DATABASE_URL is required")

DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
logger.info("Using transaction pooler connection (PgBouncer port 6543)")

# PgBouncer requires specific settings to work properly
# Solution from SQLAlchemy GitHub issue #6467 and Stack Overflow
from uuid import uuid4

connect_args = {
    "ssl": "require",  # Supabase requires SSL
    "statement_cache_size": 0,  # Critical: Must be 0 for PgBouncer
    # Generate unique statement names to avoid conflicts with PgBouncer
    "prepared_statement_name_func": lambda: f"__asyncpg_{uuid4()}__",
    "command_timeout": 60,
    "server_settings": {
        "jit": "off",  # Helps with PgBouncer compatibility
        "application_name": "swallowtail_backend"
    }
}

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
    connect_args=connect_args,
    # Additional settings for PgBouncer compatibility
    pool_recycle=3600,  # Recycle connections after 1 hour
    pool_timeout=30,  # Timeout for getting connection from pool
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Create base class for declarative models
Base = declarative_base()

# Create synchronous engine for Celery tasks
# Always use transaction pooler - direct connections don't work on Railway
sync_database_url = settings.database_url

# For sync engine with psycopg2, we need different connection args
sync_connect_args = {
    "sslmode": "require",
    "options": "-c statement_timeout=30000 -c idle_in_transaction_session_timeout=60000"
}

sync_engine = create_engine(
    sync_database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
    connect_args=sync_connect_args,
    pool_recycle=3600,
)

# Create synchronous session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=sync_engine
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db() -> None:
    """Initialize database by creating all tables."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def close_db() -> None:
    """Close database connections."""
    await engine.dispose()


def get_session() -> Generator[Session, None, None]:
    """Get synchronous database session for Celery tasks."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()