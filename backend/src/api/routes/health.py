"""Health check endpoints."""

from typing import Dict, Any, Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from ...core.state import SharedState
from ...core.tasks import check_celery_health
from ...core.database import engine, get_db
from ...core.config import get_settings

router = APIRouter()
settings = get_settings()


class DatabasePoolStatus(BaseModel):
    """Database connection pool status."""
    connected: bool
    connection_type: str  # "pooled" or "direct"
    database_url_type: str  # Which URL is being used
    pool_size: Optional[int] = None
    pool_overflow: Optional[int] = None
    pool_checked_out: Optional[int] = None
    database_name: Optional[str] = None
    postgresql_version: Optional[str] = None
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Health check response model."""
    
    status: str
    redis_connected: bool
    celery_status: Dict[str, Any]
    database_status: DatabasePoolStatus
    environment: str
    version: str = "0.1.0"


@router.get("/health", response_model=HealthResponse)
async def health_check(db: AsyncSession = Depends(get_db)) -> HealthResponse:
    """Check API health and dependencies including database connection pool."""
    
    # Check Redis connection
    try:
        state = SharedState()
        state.redis.ping()
        redis_connected = True
    except Exception:
        redis_connected = False
    
    # Check Celery status
    celery_status = check_celery_health()
    
    # Check Database connection and pool status
    database_status = await check_database_pool(db)
    
    # Determine overall health
    overall_status = "healthy"
    if not redis_connected:
        overall_status = "degraded"
    elif celery_status["status"] != "healthy":
        overall_status = "degraded"
    elif not database_status.connected:
        overall_status = "error"
    
    return HealthResponse(
        status=overall_status,
        redis_connected=redis_connected,
        celery_status=celery_status,
        database_status=database_status,
        environment=settings.environment,
    )


async def check_database_pool(db: AsyncSession) -> DatabasePoolStatus:
    """Check database connection pool status."""
    try:
        # Always using transaction pooler now for IPv4 compatibility
        connection_type = "transaction_pooler"
        database_url_type = "DATABASE_URL"
        
        # Test basic connection
        result = await db.execute(text("SELECT current_database(), version()"))
        row = result.first()
        database_name = row[0] if row else None
        postgresql_version = row[1].split()[1] if row and len(row[1].split()) > 1 else None
        
        # Get pool statistics from engine
        pool = engine.pool
        pool_status = pool.status() if hasattr(pool, 'status') else None
        
        # Parse pool status (format: "Pool size: X  Connections in pool: Y Current Overflow: Z Current Checked out connections: W")
        pool_size = None
        pool_overflow = None
        pool_checked_out = None
        
        if pool_status:
            import re
            size_match = re.search(r'Pool size: (\d+)', pool_status)
            overflow_match = re.search(r'Current Overflow: (-?\d+)', pool_status)
            checked_match = re.search(r'Current Checked out connections: (\d+)', pool_status)
            
            if size_match:
                pool_size = int(size_match.group(1))
            if overflow_match:
                pool_overflow = int(overflow_match.group(1))
            if checked_match:
                pool_checked_out = int(checked_match.group(1))
        
        return DatabasePoolStatus(
            connected=True,
            connection_type=connection_type,
            database_url_type=database_url_type,
            pool_size=pool_size,
            pool_overflow=pool_overflow,
            pool_checked_out=pool_checked_out,
            database_name=database_name,
            postgresql_version=postgresql_version,
        )
        
    except Exception as e:
        return DatabasePoolStatus(
            connected=False,
            connection_type="unknown",
            database_url_type="unknown",
            error=str(e),
        )