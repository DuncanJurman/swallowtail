
"""Celery task definitions and utilities."""
import asyncio
import functools
import logging
from typing import Any, Callable, Dict, Optional

from celery import Task
from celery.result import AsyncResult

from src.core.celery_app import celery_app

logger = logging.getLogger(__name__)


class CallbackTask(Task):
    """Task with callbacks for success and error handling."""
    
    def on_success(self, retval, task_id, args, kwargs):
        """Called on successful task completion."""
        logger.info(f"Task {task_id} completed successfully")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Called on task failure."""
        logger.error(f"Task {task_id} failed: {exc}")


def agent_task(func: Callable) -> Task:
    """Decorator for agent-specific tasks."""
    @celery_app.task(
        name=f"agent.{func.__name__}",
        base=CallbackTask,
        bind=True,
        max_retries=3,
        default_retry_delay=60
    )
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            logger.error(f"Agent task {func.__name__} failed: {exc}")
            raise self.retry(exc=exc)
    
    return wrapper


def background_task(func: Callable) -> Task:
    """Decorator for background tasks."""
    @celery_app.task(
        name=f"background.{func.__name__}",
        base=CallbackTask,
        bind=True,
        max_retries=5,
        default_retry_delay=30
    )
    @functools.wraps(func)
    def wrapper(self, *args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as exc:
            logger.error(f"Background task {func.__name__} failed: {exc}")
            raise self.retry(exc=exc)
    
    return wrapper


def check_celery_health() -> Dict[str, Any]:
    """Check Celery workers health status."""
    try:
        inspect = celery_app.control.inspect()
        stats = inspect.stats()
        
        if stats:
            return {
                "status": "healthy",
                "workers": list(stats.keys()),
                "details": stats
            }
        else:
            return {
                "status": "unhealthy",
                "workers": [],
                "error": "No active workers found"
            }
    except Exception as e:
        return {
            "status": "error",
            "workers": [],
            "error": str(e)
        }


async def execute_agent_task(
    agent_name: str,
    method: str,
    payload: Dict[str, Any],
    task_id: Optional[str] = None
) -> Dict[str, Any]:
    """Execute an agent task asynchronously."""
    task_name = f"agent.{agent_name.lower()}_{method}"
    
    # Send task to Celery
    result: AsyncResult = celery_app.send_task(
        task_name,
        args=[payload],
        task_id=task_id
    )
    
    # For async compatibility, we'll check the result in a non-blocking way
    loop = asyncio.get_event_loop()
    
    def get_result():
        return result.get(timeout=300)  # 5 minute timeout
    
    # Run the blocking operation in a thread pool
    task_result = await loop.run_in_executor(None, get_result)
    
    return task_result


# Example tasks for testing
@celery_app.task(name="test.ping")
def ping():
    """Simple ping task for testing."""
    return "pong"


@agent_task
def process_market_research(data: Dict[str, Any]) -> Dict[str, Any]:
    """Process market research data."""
    logger.info(f"Processing market research: {data}")
    # This would be replaced with actual agent logic
    return {
        "status": "completed",
        "products_found": 3,
        "data": data
    }