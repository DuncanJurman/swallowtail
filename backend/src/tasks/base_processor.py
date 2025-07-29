"""Base task processor with CrewAI integration points."""

import logging
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List
from uuid import UUID
import json
import asyncio

from celery import Task
from sqlalchemy.orm import Session

from src.core.celery_app import celery_app
from src.core.database import get_session
from src.core.websocket import ws_manager
from src.models.instance import InstanceTask, InstanceTaskStatus, TaskPriority
from src.models.instance_schemas import TaskExecutionStep

logger = logging.getLogger(__name__)


class BaseTaskProcessor(ABC):
    """Base class for all task processors."""
    
    def __init__(self, task_id: UUID, instance_id: UUID):
        self.task_id = task_id
        self.instance_id = instance_id
        self.db_session: Optional[Session] = None
        self.task: Optional[InstanceTask] = None
        
    def __enter__(self):
        """Enter context manager."""
        self.db_session = next(get_session())
        self.task = self.db_session.query(InstanceTask).filter_by(
            id=self.task_id,
            instance_id=self.instance_id
        ).first()
        
        if not self.task:
            raise ValueError(f"Task {self.task_id} not found for instance {self.instance_id}")
            
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context manager."""
        if self.db_session:
            if exc_type:
                self.db_session.rollback()
            else:
                self.db_session.commit()
            self.db_session.close()
    
    @abstractmethod
    def process(self) -> Dict[str, Any]:
        """Process the task. Must be implemented by subclasses."""
        pass
    
    def update_status(self, status: InstanceTaskStatus, error_message: Optional[str] = None):
        """Update task status in database."""
        if not self.task or not self.db_session:
            raise RuntimeError("Processor not initialized. Use within context manager.")
            
        self.task.status = status
        if error_message:
            self.task.error_message = error_message
            
        # Update timestamps
        if status == InstanceTaskStatus.IN_PROGRESS and not self.task.processing_started_at:
            self.task.processing_started_at = datetime.now(timezone.utc)
        elif status in [InstanceTaskStatus.COMPLETED, InstanceTaskStatus.FAILED]:
            self.task.processing_ended_at = datetime.now(timezone.utc)
            
        self.db_session.commit()
        
        # Broadcast status update via WebSocket
        self._broadcast_status_update(status, error_message)
    
    def update_progress(self, percentage: int, message: Optional[str] = None):
        """Update task progress."""
        if not self.task or not self.db_session:
            raise RuntimeError("Processor not initialized. Use within context manager.")
            
        self.task.progress_percentage = max(0, min(100, percentage))
        
        if message:
            # Add to execution steps
            step = {
                "step_id": f"progress_{datetime.now(timezone.utc).timestamp()}",
                "agent": self.__class__.__name__,
                "action": message,
                "status": "in_progress",
                "started_at": datetime.now(timezone.utc).isoformat()
            }
            
            if not self.task.execution_steps:
                self.task.execution_steps = []
            self.task.execution_steps.append(step)
            
        self.db_session.commit()
        
        # Broadcast progress update via WebSocket
        self._broadcast_progress_update(percentage, message)
    
    def add_execution_step(self, step: TaskExecutionStep):
        """Add an execution step to the task."""
        if not self.task or not self.db_session:
            raise RuntimeError("Processor not initialized. Use within context manager.")
            
        step_dict = step.model_dump()
        
        if not self.task.execution_steps:
            self.task.execution_steps = []
        self.task.execution_steps.append(step_dict)
        
        self.db_session.commit()
        
        # Broadcast execution step via WebSocket
        self._broadcast_execution_step(step_dict)
    
    def set_output(self, 
                  output_format: str,
                  output_data: Dict[str, Any],
                  output_media_ids: Optional[List[str]] = None):
        """Set task output."""
        if not self.task or not self.db_session:
            raise RuntimeError("Processor not initialized. Use within context manager.")
            
        self.task.output_format = output_format
        self.task.output_data = output_data
        if output_media_ids:
            self.task.output_media_ids = output_media_ids
            
        self.db_session.commit()
    
    def parse_intent(self) -> Dict[str, Any]:
        """Parse task description to extract intent."""
        # This will be enhanced with NLP/LLM integration
        # For now, return a simple structure
        return {
            "raw_description": self.task.description,
            "intent_type": "unknown",
            "entities": [],
            "confidence": 0.0
        }
    
    def _broadcast_status_update(self, status: InstanceTaskStatus, error_message: Optional[str] = None):
        """Broadcast status update via WebSocket."""
        try:
            # Run async broadcast in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                ws_manager.broadcast_task_status(
                    str(self.instance_id),
                    str(self.task_id),
                    status.value,
                    error_message
                )
            )
            loop.close()
        except Exception as e:
            logger.error(f"Failed to broadcast status update: {e}")
    
    def _broadcast_progress_update(self, percentage: int, message: Optional[str] = None):
        """Broadcast progress update via WebSocket."""
        try:
            # Run async broadcast in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                ws_manager.broadcast_task_progress(
                    str(self.instance_id),
                    str(self.task_id),
                    percentage,
                    message
                )
            )
            loop.close()
        except Exception as e:
            logger.error(f"Failed to broadcast progress update: {e}")
    
    def _broadcast_execution_step(self, step: Dict[str, Any]):
        """Broadcast execution step via WebSocket."""
        try:
            # Run async broadcast in sync context
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(
                ws_manager.broadcast_execution_step(
                    str(self.instance_id),
                    str(self.task_id),
                    step
                )
            )
            loop.close()
        except Exception as e:
            logger.error(f"Failed to broadcast execution step: {e}")


class CeleryTaskProcessor(Task):
    """Celery task wrapper for task processors."""
    
    autoretry_for = (Exception,)
    retry_kwargs = {'max_retries': 3}
    retry_backoff = True
    retry_backoff_max = 600  # 10 minutes
    retry_jitter = True
    
    def run(self, task_id: str, instance_id: str, processor_class: str):
        """Execute a task processor."""
        task_uuid = UUID(task_id)
        instance_uuid = UUID(instance_id)
        
        # Import processor class dynamically
        module_path, class_name = processor_class.rsplit('.', 1)
        module = __import__(module_path, fromlist=[class_name])
        ProcessorClass = getattr(module, class_name)
        
        # Execute processor
        with ProcessorClass(task_uuid, instance_uuid) as processor:
            try:
                processor.update_status(InstanceTaskStatus.IN_PROGRESS)
                result = processor.process()
                processor.update_status(InstanceTaskStatus.COMPLETED)
                return result
            except Exception as e:
                logger.error(f"Task {task_id} failed: {str(e)}")
                processor.update_status(InstanceTaskStatus.FAILED, str(e))
                processor.task.retry_count += 1
                raise
    
    def on_retry(self, exc, task_id, args, kwargs, einfo):
        """Handle retry event."""
        logger.warning(f"Retrying task {args[0]} due to: {exc}")
    
    def on_failure(self, exc, task_id, args, kwargs, einfo):
        """Handle final failure."""
        logger.error(f"Task {args[0]} failed permanently: {exc}")


# Register the Celery task
@celery_app.task(base=CeleryTaskProcessor, name='process_task')
def process_task(task_id: str, instance_id: str, processor_class: str):
    """Process a task using the specified processor class."""
    return CeleryTaskProcessor().run(task_id, instance_id, processor_class)