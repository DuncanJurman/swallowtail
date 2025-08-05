"""Common dependencies for API routes."""
from typing import Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database import get_db as async_get_db
from src.models.user import User


async def get_db() -> AsyncSession:
    """Get async database session."""
    async for db in async_get_db():
        yield db


async def get_current_user() -> User:
    """Get current user - placeholder for now."""
    # TODO: Implement proper authentication
    # For now, return a mock user for testing
    return User(
        id=UUID("00000000-0000-0000-0000-000000000000"),
        email="test@example.com",
        name="Test User"
    )