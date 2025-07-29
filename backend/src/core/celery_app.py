"""Celery application configuration and initialization."""
from celery import Celery
from kombu import Queue

from src.core.config import get_settings


def create_celery_app() -> Celery:
    """Create and configure Celery application."""
    settings = get_settings()
    
    # Create Celery instance
    app = Celery("swallowtail")
    
    # Configure Celery
    app.conf.update(
        broker_url=f"{settings.redis_url}/0",  # Use Redis DB 0 for broker
        result_backend=f"{settings.redis_url}/1",  # Use Redis DB 1 for results
        task_serializer="json",
        result_serializer="json",
        accept_content=["json"],
        timezone="UTC",
        enable_utc=True,
        
        # Task execution settings
        task_track_started=True,
        task_time_limit=30 * 60,  # 30 minutes
        task_soft_time_limit=25 * 60,  # 25 minutes
        task_acks_late=True,
        worker_prefetch_multiplier=1,
        
        # Result backend settings
        result_expires=3600,  # 1 hour
        
        # Queue configuration
        task_default_queue="default",
        task_queues=(
            Queue("default", routing_key="default"),
            Queue("agents", routing_key="agent.*"),
            Queue("background", routing_key="background.*"),
        ),
        task_routes={
            "agent.*": {"queue": "agents"},
            "background.*": {"queue": "background"},
        },
    )
    
    # Auto-discover tasks
    app.autodiscover_tasks(["src.core", "src.agents"])
    
    return app


# Create global Celery instance
celery_app = create_celery_app()