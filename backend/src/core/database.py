"""Database configuration and connection management."""

from typing import AsyncGenerator, Generator

from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import declarative_base, sessionmaker, Session

from src.core.config import get_settings


settings = get_settings()

# Use asyncpg for better performance with PostgreSQL
DATABASE_URL = settings.database_url.replace("postgresql://", "postgresql+asyncpg://") if settings.database_url else None

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=10,
    max_overflow=20,
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
sync_engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
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