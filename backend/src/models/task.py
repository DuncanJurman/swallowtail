"""Task models for product task management."""

from datetime import datetime
from typing import Optional, Dict, Any
from uuid import UUID
from enum import Enum

from pydantic import BaseModel, Field

from ..models.database import TaskStatus


class TaskPriority(int, Enum):
    """Task priority levels."""
    URGENT = 1
    HIGH = 3
    MEDIUM = 5
    LOW = 7
    TRIVIAL = 9


class ProductTaskBase(BaseModel):
    """Base model for product tasks."""
    task_description: str = Field(..., description="Natural language description of the task")
    priority: TaskPriority = Field(TaskPriority.MEDIUM, description="Task priority (1=urgent, 9=trivial)")


class TaskCreateRequest(ProductTaskBase):
    """Request model for creating a new task."""
    pass


class TaskUpdateRequest(BaseModel):
    """Request model for updating a task."""
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None
    assigned_agent: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None


class ProductTask(ProductTaskBase):
    """Complete product task model."""
    id: UUID
    product_id: UUID
    status: TaskStatus
    assigned_agent: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: datetime
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_by: Optional[UUID] = None
    
    class Config:
        from_attributes = True


class TaskResponse(ProductTask):
    """API response model for a task."""
    # Can include computed fields
    duration_seconds: Optional[float] = None
    
    def __init__(self, **data):
        super().__init__(**data)
        # Calculate duration if both started and completed
        if self.started_at and self.completed_at:
            self.duration_seconds = (self.completed_at - self.started_at).total_seconds()


class TaskListResponse(BaseModel):
    """Response model for listing tasks."""
    tasks: list[TaskResponse]
    total: int
    page: int = 1
    page_size: int = 50


class TaskStatusUpdate(BaseModel):
    """Model for updating task status."""
    status: TaskStatus
    message: Optional[str] = None
    result_data: Optional[Dict[str, Any]] = None