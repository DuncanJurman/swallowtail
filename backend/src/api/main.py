"""FastAPI application setup."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from ..core.config import get_settings
from .routes import agents, checkpoints, health

settings = get_settings()


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="Swallowtail API",
        description="Autonomous multi-agent e-commerce platform",
        version="0.1.0",
        docs_url="/docs" if settings.debug else None,
        redoc_url="/redoc" if settings.debug else None,
    )
    
    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include routers
    app.include_router(health.router, tags=["health"])
    app.include_router(
        agents.router,
        prefix=f"{settings.api_prefix}/agents",
        tags=["agents"]
    )
    app.include_router(
        checkpoints.router,
        prefix=f"{settings.api_prefix}/checkpoints",
        tags=["checkpoints"]
    )
    
    return app


app = create_app()