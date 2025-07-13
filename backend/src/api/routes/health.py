"""Health check endpoints."""

from fastapi import APIRouter
from pydantic import BaseModel

from ...core.state import SharedState

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str
    redis_connected: bool
    version: str = "0.1.0"


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check API health and dependencies."""
    try:
        # Test Redis connection
        state = SharedState()
        state.redis.ping()
        redis_connected = True
    except Exception:
        redis_connected = False
    
    return HealthResponse(
        status="healthy" if redis_connected else "degraded",
        redis_connected=redis_connected,
    )