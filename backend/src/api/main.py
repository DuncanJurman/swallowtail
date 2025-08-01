"""FastAPI application setup."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import socketio

from ..core.config import get_settings
from ..core.websocket import sio as socketio_server
from .routes import checkpoints, health, image_generation, tasks, tiktok
from . import instances

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
        checkpoints.router,
        prefix=f"{settings.api_prefix}/checkpoints",
        tags=["checkpoints"]
    )
    app.include_router(
        image_generation.router,
        prefix=settings.api_prefix,
        tags=["image-generation"]
    )
    app.include_router(
        instances.router,
        prefix=settings.api_prefix,
        tags=["instances"]
    )
    app.include_router(
        tasks.router,
        prefix=settings.api_prefix,
        tags=["tasks"]
    )
    app.include_router(
        tiktok.router,
        prefix=settings.api_prefix,
        tags=["tiktok"]
    )
    
    return app


# Create FastAPI app
app = create_app()

# Create Socket.io ASGI app wrapper
socket_app = socketio.ASGIApp(socketio_server, app)

# Export the socket_app for uvicorn to use
__all__ = ['app', 'socket_app']