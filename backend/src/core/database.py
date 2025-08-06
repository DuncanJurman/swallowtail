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

# Determine which connection to use based on environment
# Production should use pooled connection for better resource management
# Development can use direct connection if available
use_pooled = (
    os.getenv("USE_POOLED_CONNECTION", "").lower() == "true" 
    or settings.environment == "production"
    or not settings.database_direct_url  # If no direct URL, must use pooled
)

if use_pooled:
    # Use pooled connection (PgBouncer on port 6543)
    if not settings.database_url:
        raise ValueError("DATABASE_URL is required for pooled connection")
    
    DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://")
    logger.info("Using pooled database connection (PgBouncer)")
    
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
else:
    # Use direct connection (port 5432) - only for development or migrations
    DATABASE_URL = settings.database_direct_url.replace("postgresql://", "postgresql+asyncpg://")
    logger.info("Using direct database connection")
    
    # Direct connection can use prepared statements for better performance
    connect_args = {
        "ssl": "require",
        "command_timeout": 60,
        "server_settings": {
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
# Sync engine should also use the pooled connection in production
sync_database_url = settings.database_url if use_pooled else settings.database_direct_url

# For sync engine with psycopg2, we need different connection args
if use_pooled:
    sync_connect_args = {
        "sslmode": "require",
        "options": "-c statement_timeout=30000 -c idle_in_transaction_session_timeout=60000"
    }
else:
    sync_connect_args = {
        "sslmode": "require"
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