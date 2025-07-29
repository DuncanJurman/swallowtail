"""Enhanced task API endpoints with filtering and queue integration."""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks, status
from sqlalchemy.orm import Session

from src.core.sync_database import get_db
from src.tasks.queue_service import TaskQueueService
from src.models.instance import Instance, InstanceTask, InstanceTaskStatus, TaskPriority
from src.models.instance_schemas import (
    TaskSubmission, 
    InstanceTaskResponse, 
    TaskListFilters,
    TaskUpdateRequest
)

router = APIRouter(prefix="/tasks", tags=["tasks"])


def get_current_user_id() -> UUID:
    """Get the current user ID from auth context."""
    # TODO: Implement actual authentication
    # For now, return a fixed UUID for testing
    return UUID("00000000-0000-0000-0000-000000000001")


def verify_instance_access(
    instance_id: UUID,
    user_id: UUID,
    db: Session
) -> Instance:
    """Verify user has access to the instance."""
    instance = db.query(Instance).filter(
        Instance.id == instance_id,
        Instance.user_id == user_id
    ).first()
    
    if not instance:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Instance not found or access denied"
        )
    
    return instance


def verify_task_access(
    task_id: UUID,
    user_id: UUID,
    db: Session
) -> InstanceTask:
    """Verify user has access to the task."""
    task = db.query(InstanceTask).join(Instance).filter(
        InstanceTask.id == task_id,
        Instance.user_id == user_id
    ).first()
    
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found or access denied"
        )
    
    return task


@router.post("/instances/{instance_id}/tasks", 
             response_model=InstanceTaskResponse,
             status_code=status.HTTP_201_CREATED)
def submit_task(
    instance_id: UUID,
    task_data: TaskSubmission,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Submit a new task to the queue."""
    # Verify access
    instance = verify_instance_access(instance_id, user_id, db)
    
    # Submit task through queue service
    queue_service = TaskQueueService(db)
    task = queue_service.submit_task(instance_id, task_data)
    
    # Process scheduled tasks in background
    if not task_data.scheduled_for or task_data.scheduled_for <= datetime.now():
        background_tasks.add_task(process_scheduled_tasks, db)
    
    return task


@router.get("/instances/{instance_id}/tasks",
            response_model=List[InstanceTaskResponse])
def list_tasks(
    instance_id: UUID,
    status: Optional[InstanceTaskStatus] = Query(None),
    priority: Optional[TaskPriority] = Query(None),
    created_after: Optional[datetime] = Query(None),
    created_before: Optional[datetime] = Query(None),
    scheduled_after: Optional[datetime] = Query(None),
    scheduled_before: Optional[datetime] = Query(None),
    limit: int = Query(50, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """List tasks with advanced filtering."""
    # Verify access
    instance = verify_instance_access(instance_id, user_id, db)
    
    # Create filters
    filters = TaskListFilters(
        status=status,
        priority=priority,
        created_after=created_after,
        created_before=created_before,
        scheduled_after=scheduled_after,
        scheduled_before=scheduled_before,
        limit=limit,
        offset=offset
    )
    
    # Get tasks through queue service
    queue_service = TaskQueueService(db)
    tasks = queue_service.list_tasks(instance_id, filters)
    
    return tasks


@router.get("/tasks/{task_id}",
            response_model=InstanceTaskResponse)
def get_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Get task details with current status."""
    task = verify_task_access(task_id, user_id, db)
    return task


@router.get("/tasks/{task_id}/status")
def get_task_status(
    task_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Get detailed task status including Celery information."""
    task = verify_task_access(task_id, user_id, db)
    
    queue_service = TaskQueueService(db)
    status = queue_service.get_task_status(task_id)
    
    return status


@router.patch("/tasks/{task_id}",
              response_model=InstanceTaskResponse)
def update_task(
    task_id: UUID,
    update_data: TaskUpdateRequest,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Update task properties (priority, status, etc)."""
    task = verify_task_access(task_id, user_id, db)
    
    queue_service = TaskQueueService(db)
    updated_task = queue_service.update_task(task_id, update_data)
    
    return updated_task


@router.post("/tasks/{task_id}/cancel",
             status_code=status.HTTP_204_NO_CONTENT)
def cancel_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Cancel a pending or running task."""
    task = verify_task_access(task_id, user_id, db)
    
    queue_service = TaskQueueService(db)
    success = queue_service.cancel_task(task_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Task cannot be cancelled in its current state"
        )
    
    return


@router.post("/tasks/{task_id}/retry",
             response_model=InstanceTaskResponse)
def retry_task(
    task_id: UUID,
    db: Session = Depends(get_db),
    user_id: UUID = Depends(get_current_user_id)
):
    """Retry a failed task."""
    task = verify_task_access(task_id, user_id, db)
    
    queue_service = TaskQueueService(db)
    
    try:
        retried_task = queue_service.retry_task(task_id)
        return retried_task
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/process-scheduled",
             include_in_schema=False)
def trigger_scheduled_processing(
    db: Session = Depends(get_db)
):
    """Manually trigger processing of scheduled tasks (admin endpoint)."""
    queue_service = TaskQueueService(db)
    count = queue_service.process_scheduled_tasks()
    
    return {"processed": count}


def process_scheduled_tasks(db: Session):
    """Background task to process scheduled tasks."""
    try:
        queue_service = TaskQueueService(db)
        queue_service.process_scheduled_tasks()
    except Exception as e:
        print(f"Error processing scheduled tasks: {e}")


# Register processors on import
def register_task_processors():
    """Register all task processors with the queue service."""
    from src.tasks.processors.default_processor import DefaultTaskProcessor
    from src.tasks.processors.content_creation_processor import ContentCreationProcessor
    
    # Register processors
    TaskQueueService.register_processor('default', DefaultTaskProcessor)
    TaskQueueService.register_processor('general', DefaultTaskProcessor)
    TaskQueueService.register_processor('content_creation', ContentCreationProcessor)


# Register processors when module is imported
register_task_processors()