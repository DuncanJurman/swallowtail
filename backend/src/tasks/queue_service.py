"""Task queue service for managing task lifecycle."""

import logging
from datetime import datetime, timezone
from typing import Dict, Any, Optional, List, Type
from uuid import UUID

from sqlalchemy.orm import Session
from celery.result import AsyncResult

from src.core.celery_app import celery_app
from src.core.database import get_session
from src.models.instance import (
    Instance, InstanceTask, InstanceTaskStatus, TaskPriority
)
from src.models.instance_schemas import TaskSubmission, TaskListFilters, TaskUpdateRequest
from src.tasks.base_processor import BaseTaskProcessor

logger = logging.getLogger(__name__)


class TaskQueueService:
    """Service for managing task queue operations."""
    
    # Registry of task processors
    _processor_registry: Dict[str, Type[BaseTaskProcessor]] = {}
    
    @classmethod
    def register_processor(cls, intent_type: str, processor_class: Type[BaseTaskProcessor]):
        """Register a task processor for a specific intent type."""
        cls._processor_registry[intent_type] = processor_class
        logger.info(f"Registered processor {processor_class.__name__} for intent type: {intent_type}")
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def submit_task(self, instance_id: UUID, submission: TaskSubmission) -> InstanceTask:
        """Submit a new task to the queue."""
        # Verify instance exists
        instance = self.db_session.query(Instance).filter_by(id=instance_id).first()
        if not instance:
            raise ValueError(f"Instance {instance_id} not found")
        
        # Create task record
        task = InstanceTask(
            instance_id=instance_id,
            description=submission.description,
            priority=submission.priority,
            scheduled_for=submission.scheduled_for,
            recurring_pattern=submission.recurring_pattern,
            attached_media_ids=submission.attached_media_ids,
            status=InstanceTaskStatus.SUBMITTED
        )
        
        self.db_session.add(task)
        self.db_session.commit()
        
        # Queue for processing if not scheduled
        if not submission.scheduled_for or submission.scheduled_for <= datetime.now(timezone.utc):
            self._queue_task(task)
        
        return task
    
    def _queue_task(self, task: InstanceTask):
        """Queue a task for processing."""
        # Parse intent to determine processor
        intent_type = self._parse_intent_type(task.description)
        processor_class = self._processor_registry.get(intent_type)
        
        if not processor_class:
            # Use default processor
            processor_class = self._processor_registry.get('default')
            if not processor_class:
                logger.error(f"No processor found for intent type: {intent_type}")
                task.status = InstanceTaskStatus.FAILED
                task.error_message = f"No processor available for intent type: {intent_type}"
                self.db_session.commit()
                return
        
        # Update task status
        task.status = InstanceTaskStatus.QUEUED
        task.parsed_intent = {
            "intent_type": intent_type,
            "processor": processor_class.__name__
        }
        self.db_session.commit()
        
        # Determine queue based on priority
        queue_name = self._get_queue_name(task.priority)
        
        # Submit to Celery
        processor_path = f"{processor_class.__module__}.{processor_class.__name__}"
        result = celery_app.send_task(
            'process_task',
            args=[str(task.id), str(task.instance_id), processor_path],
            queue=queue_name,
            task_id=f"task_{task.id}"
        )
        
        logger.info(f"Queued task {task.id} to {queue_name} queue with processor {processor_class.__name__}")
    
    def _parse_intent_type(self, description: str) -> str:
        """Parse task description to determine intent type."""
        # This will be enhanced with NLP/LLM integration
        # For now, use simple keyword matching
        description_lower = description.lower()
        
        if any(word in description_lower for word in ['post', 'content', 'social']):
            return 'content_creation'
        elif any(word in description_lower for word in ['analyze', 'research', 'market']):
            return 'market_analysis'
        elif any(word in description_lower for word in ['email', 'campaign', 'newsletter']):
            return 'email_campaign'
        elif any(word in description_lower for word in ['product', 'listing', 'inventory']):
            return 'product_management'
        else:
            return 'general'
    
    def _get_queue_name(self, priority: TaskPriority) -> str:
        """Get queue name based on priority."""
        if priority == TaskPriority.URGENT:
            return 'agents'  # High priority queue
        elif priority == TaskPriority.LOW:
            return 'background'
        else:
            return 'default'
    
    def get_task_status(self, task_id: UUID) -> Dict[str, Any]:
        """Get current status of a task."""
        task = self.db_session.query(InstanceTask).filter_by(id=task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Get Celery task status if queued or processing
        celery_status = None
        if task.status in [InstanceTaskStatus.QUEUED, InstanceTaskStatus.IN_PROGRESS]:
            try:
                result = AsyncResult(f"task_{task_id}", app=celery_app)
                celery_status = {
                    "state": result.state,
                    "info": result.info if result.info else {}
                }
            except Exception as e:
                logger.error(f"Error getting Celery status for task {task_id}: {e}")
        
        return {
            "task_id": task.id,
            "status": task.status,
            "progress": task.progress_percentage,
            "execution_steps": task.execution_steps,
            "celery_status": celery_status,
            "error_message": task.error_message,
            "created_at": task.created_at,
            "processing_started_at": task.processing_started_at,
            "processing_ended_at": task.processing_ended_at
        }
    
    def update_task(self, task_id: UUID, update: TaskUpdateRequest) -> InstanceTask:
        """Update task details."""
        task = self.db_session.query(InstanceTask).filter_by(id=task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Update fields
        if update.status:
            task.status = update.status
        if update.priority:
            task.priority = update.priority
        if update.progress_percentage is not None:
            task.progress_percentage = update.progress_percentage
        if update.error_message:
            task.error_message = update.error_message
        if update.execution_step:
            if not task.execution_steps:
                task.execution_steps = []
            task.execution_steps.append(update.execution_step.model_dump())
        
        self.db_session.commit()
        return task
    
    def cancel_task(self, task_id: UUID) -> bool:
        """Cancel a task."""
        task = self.db_session.query(InstanceTask).filter_by(id=task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Can only cancel if not completed
        if task.status in [InstanceTaskStatus.COMPLETED, InstanceTaskStatus.FAILED]:
            return False
        
        # Try to revoke Celery task
        if task.status in [InstanceTaskStatus.QUEUED, InstanceTaskStatus.IN_PROGRESS]:
            try:
                celery_app.control.revoke(f"task_{task_id}", terminate=True)
            except Exception as e:
                logger.error(f"Error revoking Celery task {task_id}: {e}")
        
        # Update status
        task.status = InstanceTaskStatus.CANCELLED
        task.processing_ended_at = datetime.now(timezone.utc)
        self.db_session.commit()
        
        return True
    
    def retry_task(self, task_id: UUID) -> InstanceTask:
        """Retry a failed task."""
        task = self.db_session.query(InstanceTask).filter_by(id=task_id).first()
        if not task:
            raise ValueError(f"Task {task_id} not found")
        
        # Can only retry failed tasks
        if task.status != InstanceTaskStatus.FAILED:
            raise ValueError(f"Can only retry failed tasks. Current status: {task.status}")
        
        # Reset task for retry
        task.status = InstanceTaskStatus.SUBMITTED
        task.error_message = None
        task.processing_started_at = None
        task.processing_ended_at = None
        task.retry_count += 1
        
        self.db_session.commit()
        
        # Queue for processing
        self._queue_task(task)
        
        return task
    
    def list_tasks(self, instance_id: UUID, filters: TaskListFilters) -> List[InstanceTask]:
        """List tasks with filters."""
        query = self.db_session.query(InstanceTask).filter_by(instance_id=instance_id)
        
        # Apply filters
        if filters.status:
            query = query.filter(InstanceTask.status == filters.status)
        if filters.priority:
            query = query.filter(InstanceTask.priority == filters.priority)
        if filters.created_after:
            query = query.filter(InstanceTask.created_at >= filters.created_after)
        if filters.created_before:
            query = query.filter(InstanceTask.created_at <= filters.created_before)
        if filters.scheduled_after:
            query = query.filter(InstanceTask.scheduled_for >= filters.scheduled_after)
        if filters.scheduled_before:
            query = query.filter(InstanceTask.scheduled_for <= filters.scheduled_before)
        
        # Order by creation date desc
        query = query.order_by(InstanceTask.created_at.desc())
        
        # Apply pagination
        query = query.limit(filters.limit).offset(filters.offset)
        
        return query.all()
    
    def process_scheduled_tasks(self):
        """Process tasks that are due for execution."""
        # Find tasks that are scheduled and due
        due_tasks = self.db_session.query(InstanceTask).filter(
            InstanceTask.status == InstanceTaskStatus.SUBMITTED,
            InstanceTask.scheduled_for <= datetime.now(timezone.utc)
        ).all()
        
        for task in due_tasks:
            try:
                self._queue_task(task)
                logger.info(f"Queued scheduled task {task.id}")
            except Exception as e:
                logger.error(f"Error queuing scheduled task {task.id}: {e}")
                task.status = InstanceTaskStatus.FAILED
                task.error_message = str(e)
        
        self.db_session.commit()
        
        return len(due_tasks)