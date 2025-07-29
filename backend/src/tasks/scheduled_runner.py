"""Scheduled task runner for processing due tasks."""

import logging
from datetime import datetime, timezone
from celery import Task
from celery.schedules import crontab

from src.core.celery_app import celery_app
from src.core.database import SessionLocal
from src.tasks.queue_service import TaskQueueService

logger = logging.getLogger(__name__)


@celery_app.task(name='process_scheduled_tasks')
def process_scheduled_tasks():
    """Process all scheduled tasks that are due for execution."""
    logger.info("Starting scheduled task processing")
    
    db = SessionLocal()
    try:
        queue_service = TaskQueueService(db)
        count = queue_service.process_scheduled_tasks()
        logger.info(f"Processed {count} scheduled tasks")
        return {"processed": count, "timestamp": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        logger.error(f"Error processing scheduled tasks: {e}")
        raise
    finally:
        db.close()


# Configure periodic task
celery_app.conf.beat_schedule = {
    'process-scheduled-tasks': {
        'task': 'process_scheduled_tasks',
        'schedule': crontab(minute='*/5'),  # Run every 5 minutes
    },
}