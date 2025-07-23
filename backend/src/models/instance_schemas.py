"""Pydantic schemas for instance-related API models."""

from datetime import datetime, timezone
from typing import Optional, List, Dict, Any, Literal
from uuid import UUID
from pydantic import BaseModel, Field, ConfigDict, field_validator

from src.models.instance import InstanceType, InstanceTaskStatus, TaskPriority


# Instance Models
class InstanceCreate(BaseModel):
    """Request model for creating a new instance."""
    name: str = Field(..., min_length=1, max_length=255)
    type: InstanceType
    business_profile: Dict[str, Any] = Field(..., description="Business context and brand info")


class InstanceResponse(BaseModel):
    """Response model for instance data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    name: str
    type: InstanceType
    business_profile: Dict[str, Any]
    configuration: Dict[str, Any]
    created_at: datetime
    updated_at: datetime


# Task Models
class TaskSubmission(BaseModel):
    """Request model for submitting a new task."""
    description: str = Field(..., min_length=1, description="Natural language task description")
    priority: TaskPriority = Field(default=TaskPriority.NORMAL, description="Task priority level")
    scheduled_for: Optional[datetime] = Field(None, description="When to execute the task")
    recurring_pattern: Optional[Dict[str, Any]] = Field(None, description="RRULE pattern for recurring tasks")
    attached_media_ids: List[UUID] = Field(default_factory=list, description="Reference media for the task")
    
    @field_validator('scheduled_for')
    @classmethod
    def validate_scheduled_time(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Ensure scheduled time is in the future."""
        if v and v < datetime.now(timezone.utc):
            raise ValueError("Scheduled time must be in the future")
        return v


class InstanceTaskResponse(BaseModel):
    """Response model for task data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    instance_id: UUID
    description: str
    status: InstanceTaskStatus
    priority: TaskPriority
    scheduled_for: Optional[datetime]
    recurring_pattern: Optional[Dict[str, Any]]
    
    # Structured task data
    parsed_intent: Optional[Dict[str, Any]]
    execution_steps: List[Dict[str, Any]]
    progress_percentage: int
    
    # Results
    output_format: Optional[str]
    output_data: Optional[Dict[str, Any]]
    output_media_ids: List[UUID]
    error_message: Optional[str]
    
    # Media
    attached_media_ids: List[UUID]
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    processing_started_at: Optional[datetime]
    processing_ended_at: Optional[datetime]
    
    # Metadata
    retry_count: int
    parent_task_id: Optional[UUID]


class TaskUpdateRequest(BaseModel):
    """Request model for updating task status or progress."""
    status: Optional[InstanceTaskStatus] = None
    priority: Optional[TaskPriority] = None
    progress_percentage: Optional[int] = Field(None, ge=0, le=100)
    execution_step: Optional['TaskExecutionStep'] = None
    error_message: Optional[str] = None
    

class TaskExecutionStep(BaseModel):
    """Model for a single execution step in a task."""
    step_id: str = Field(..., description="Unique identifier for this step")
    agent: str = Field(..., description="Agent or processor handling this step")
    action: str = Field(..., description="Description of the action being performed")
    status: Literal["pending", "in_progress", "completed", "failed"] = Field(..., description="Step status")
    output: Optional[Dict[str, Any]] = Field(None, description="Output from this step")
    error: Optional[str] = Field(None, description="Error message if step failed")
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    

class TaskListFilters(BaseModel):
    """Filters for listing tasks."""
    status: Optional[InstanceTaskStatus] = None
    priority: Optional[TaskPriority] = None
    created_after: Optional[datetime] = None
    created_before: Optional[datetime] = None
    scheduled_after: Optional[datetime] = None
    scheduled_before: Optional[datetime] = None
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
    

# Media Models
class InstanceMediaResponse(BaseModel):
    """Response model for media data."""
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    instance_id: UUID
    filename: str
    file_type: str
    storage_path: str
    public_url: Optional[str]
    media_category: str
    uploaded_at: datetime