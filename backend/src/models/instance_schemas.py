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
    scheduled_for: Optional[datetime] = None
    recurring_pattern: Optional[Dict[str, Any]] = None
    
    # Structured task data
    parsed_intent: Optional[Dict[str, Any]] = None
    execution_steps: List[Dict[str, Any]] = Field(default_factory=list)
    progress_percentage: int = 0
    
    # Results
    output_format: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    output_media_ids: List[UUID] = Field(default_factory=list)
    error_message: Optional[str] = None
    
    # TikTok posting fields (optional - only for content tasks)
    tiktok_post_status: Optional[str] = None
    tiktok_publish_id: Optional[str] = None
    tiktok_post_url: Optional[str] = None
    
    # Media
    attached_media_ids: List[UUID] = Field(default_factory=list)
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    processing_started_at: Optional[datetime] = None
    processing_ended_at: Optional[datetime] = None
    
    # Metadata
    retry_count: int = 0
    parent_task_id: Optional[UUID] = None


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


# Task Detail Models for TikTok Integration
class TaskPlanningStep(BaseModel):
    """A single step in the task planning phase."""
    id: str
    title: str
    description: str
    status: Literal["completed", "pending", "in_progress"] = "pending"
    reference_images: List[str] = Field(default_factory=list)


class TaskExecutionLog(BaseModel):
    """A log entry from agent execution."""
    timestamp: datetime
    agent_name: str
    action: str
    status: Literal["info", "success", "warning", "error"]
    message: str
    details: Optional[Dict[str, Any]] = None


class TaskDetailResponse(BaseModel):
    """Detailed response for a single task including planning and execution data."""
    model_config = ConfigDict(from_attributes=True)
    
    # Core task fields
    id: UUID
    instance_id: UUID
    description: str
    status: InstanceTaskStatus
    priority: TaskPriority
    
    # Planning section (generated for all tasks)
    planning: List[TaskPlanningStep] = Field(default_factory=list)
    
    # Execution logs (from execution_steps in DB)
    execution_logs: List[TaskExecutionLog] = Field(default_factory=list)
    
    # Output (may contain video_url for content creation tasks)
    output_format: Optional[str] = None
    output_data: Optional[Dict[str, Any]] = None
    output_media_ids: List[UUID] = Field(default_factory=list)
    
    # Suggested caption (extracted from output_data if available)
    suggested_caption: Optional[str] = None
    
    # Media attachments
    attached_media: List[InstanceMediaResponse] = Field(default_factory=list)
    
    # TikTok posting fields (only present if task has TikTok content)
    tiktok_post_data: Optional[Dict[str, Any]] = None
    tiktok_publish_id: Optional[str] = None
    tiktok_post_status: Optional[str] = None  # Can be None, PENDING, PROCESSING, PUBLISHED, FAILED
    tiktok_post_url: Optional[str] = None
    can_post_to_tiktok: bool = False  # Helper field to indicate if posting is available
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    processing_started_at: Optional[datetime] = None
    processing_ended_at: Optional[datetime] = None
    scheduled_post_time: Optional[datetime] = None
    
    # Error info
    error_message: Optional[str] = None


# TikTok Posting Models
class TikTokPostRequest(BaseModel):
    """Request model for posting content to TikTok."""
    title: str = Field(..., max_length=2200, description="Video caption with hashtags and mentions")
    privacy_level: Literal["PUBLIC_TO_EVERYONE", "MUTUAL_FOLLOW_FRIENDS", "FOLLOWER_OF_CREATOR", "SELF_ONLY"] = Field(
        default="SELF_ONLY",
        description="Privacy level for the post (defaults to SELF_ONLY in sandbox mode)"
    )
    disable_duet: bool = Field(default=False, description="Disable duets for this post")
    disable_stitch: bool = Field(default=False, description="Disable stitches for this post")
    disable_comment: bool = Field(default=False, description="Disable comments for this post")
    video_cover_timestamp_ms: Optional[int] = Field(None, description="Frame to use as video cover (in milliseconds)")
    account_id: Optional[UUID] = Field(None, description="Specific TikTok account ID to use (for multi-account)")
    schedule_time: Optional[datetime] = Field(None, description="When to post (future feature)")
    
    @field_validator('title')
    @classmethod
    def validate_title_length(cls, v: str) -> str:
        """Ensure title doesn't exceed TikTok's character limit."""
        if len(v) > 2200:
            raise ValueError("Title cannot exceed 2200 characters")
        return v


class TikTokPostResponse(BaseModel):
    """Response model after initiating TikTok post."""
    success: bool
    publish_id: Optional[str] = None
    status: str  # PROCESSING, PUBLISHED, FAILED
    message: str
    task_id: UUID
    estimated_completion_time: Optional[int] = Field(None, description="Estimated seconds until post is complete")


class TikTokPostStatusResponse(BaseModel):
    """Response model for checking TikTok post status."""
    publish_id: str
    status: Literal["PROCESSING_UPLOAD", "PROCESSING_DOWNLOAD", "PROCESSING", "PUBLISH_COMPLETE", "FAILED"]
    fail_reason: Optional[str] = None
    post_url: Optional[str] = None
    post_id: Optional[str] = None
    uploaded_bytes: Optional[int] = None
    downloaded_bytes: Optional[int] = None
    last_checked: datetime