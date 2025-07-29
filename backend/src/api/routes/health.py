"""Health check endpoints."""

from typing import Dict, Any
from fastapi import APIRouter
from pydantic import BaseModel

from ...core.state import SharedState
from ...core.tasks import check_celery_health

router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str
    redis_connected: bool
    celery_status: Dict[str, Any]
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
    
    # Check Celery status
    celery_status = check_celery_health()
    
    # Determine overall health
    overall_status = "healthy"
    if not redis_connected:
        overall_status = "degraded"
    elif celery_status["status"] != "healthy":
        overall_status = "degraded"
    
    return HealthResponse(
        status=overall_status,
        redis_connected=redis_connected,
        celery_status=celery_status,
    )