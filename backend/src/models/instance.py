"""Database models for instance management in Swallowtail."""

from datetime import datetime, timezone
import uuid
import enum

from sqlalchemy import Column, String, DateTime, Boolean, JSON, ForeignKey, Text, Enum as SQLEnum, Integer, Index
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from src.core.database import Base


class InstanceType(str, enum.Enum):
    """Types of business instances."""
    ECOMMERCE = "ecommerce"
    SOCIAL_MEDIA = "social_media"


class InstanceTaskStatus(str, enum.Enum):
    """Instance task execution status."""
    SUBMITTED = "submitted"
    QUEUED = "queued"
    PLANNING = "planning"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    REVIEW = "review"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class TaskPriority(str, enum.Enum):
    """Task priority levels."""
    URGENT = "urgent"
    NORMAL = "normal"
    LOW = "low"


class Instance(Base):
    """Business or brand instance with isolated configuration and agents."""
    __tablename__ = "instances"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    name = Column(String(255), nullable=False)
    type = Column(SQLEnum(InstanceType), nullable=False)
    
    # Business profile - stores context about the business
    business_profile = Column(JSONB, default=dict, nullable=False)
    
    # Configuration
    configuration = Column(JSONB, default=dict, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="instances")
    agents = relationship("InstanceAgent", back_populates="instance", cascade="all, delete-orphan")
    tasks = relationship("InstanceTask", back_populates="instance", cascade="all, delete-orphan")
    media = relationship("InstanceMedia", back_populates="instance", cascade="all, delete-orphan")
    
    # Indexes
    __table_args__ = (
        Index('idx_instances_user_id', 'user_id'),
    )


class InstanceAgent(Base):
    """Agent configuration specific to an instance."""
    __tablename__ = "instance_agents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("instances.id", ondelete="CASCADE"), nullable=False)
    agent_type = Column(String(100), nullable=False)  # manager, content_creator, etc.
    
    # Configuration
    base_config = Column(JSONB, nullable=False)  # From YAML templates
    custom_config = Column(JSONB, default=dict, nullable=False)  # User customizations
    
    # Status
    is_enabled = Column(Boolean, default=True, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    instance = relationship("Instance", back_populates="agents")
    
    # Constraints
    __table_args__ = (
        Index('idx_instance_agents_instance_id', 'instance_id'),
        Index('idx_instance_agents_type', 'instance_id', 'agent_type', unique=True),
    )


class InstanceTask(Base):
    """Tasks submitted by users for instance agents to execute."""
    __tablename__ = "instance_tasks"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("instances.id", ondelete="CASCADE"), nullable=False)
    
    # Task details
    description = Column(Text, nullable=False)
    status = Column(SQLEnum(InstanceTaskStatus), default=InstanceTaskStatus.SUBMITTED, nullable=False)
    priority = Column(SQLEnum(TaskPriority), default=TaskPriority.NORMAL, nullable=False)
    
    # Scheduling
    scheduled_for = Column(DateTime, nullable=True)  # When to execute the task
    recurring_pattern = Column(JSONB, nullable=True)  # RRULE format for recurring tasks
    
    # Structured task data
    parsed_intent = Column(JSONB, nullable=True)  # {intent, platforms, entities, parameters}
    execution_steps = Column(JSONB, default=list, nullable=False)  # [{step_id, agent, action, status, output, timestamp}]
    progress_percentage = Column(Integer, default=0, nullable=False)
    
    # Results
    output_format = Column(String(50), nullable=True)  # text, json, media, mixed
    output_data = Column(JSONB, nullable=True)  # Structured output from agents
    output_media_ids = Column(JSONB, default=list, nullable=False)  # Generated media IDs
    result_data = Column(JSONB, nullable=True)  # Legacy field - will be deprecated
    error_message = Column(Text, nullable=True)
    
    # TikTok Posting Fields
    tiktok_post_data = Column(JSONB, nullable=True)  # Metadata for TikTok post
    tiktok_publish_id = Column(String(255), nullable=True)  # TikTok's publish ID
    tiktok_post_status = Column(String(50), nullable=True)  # PENDING, PROCESSING, PUBLISHED, FAILED
    tiktok_post_url = Column(String(500), nullable=True)  # Final TikTok post URL
    scheduled_post_time = Column(DateTime, nullable=True)  # When to post to TikTok
    
    # Media attachments
    attached_media_ids = Column(JSONB, default=list, nullable=False)  # List of InstanceMedia IDs
    
    # Processing metadata
    processing_started_at = Column(DateTime, nullable=True)
    processing_ended_at = Column(DateTime, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    parent_task_id = Column(UUID(as_uuid=True), nullable=True)  # For subtasks
    
    # Timestamps
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc), nullable=False)
    started_at = Column(DateTime, nullable=True)  # Legacy - use processing_started_at
    completed_at = Column(DateTime, nullable=True)  # Legacy - use processing_ended_at
    
    # Relationships
    instance = relationship("Instance", back_populates="tasks")
    
    # Indexes
    __table_args__ = (
        Index('idx_instance_tasks_instance_status', 'instance_id', 'status'),
        Index('idx_instance_tasks_created', 'instance_id', 'created_at'),
        Index('idx_instance_tasks_priority', 'instance_id', 'priority', 'created_at'),
        Index('idx_instance_tasks_scheduled', 'scheduled_for', 'status'),
    )
    
    # Helper methods for TikTok posting
    def get_video_url(self) -> str | None:
        """Extract video URL from output_data."""
        if not self.output_data:
            return None
        
        # Check for video_url in output_data
        if isinstance(self.output_data, dict):
            return self.output_data.get('video_url') or self.output_data.get('media_url')
        
        return None
    
    def can_post_to_tiktok(self) -> bool:
        """Check if task is ready for TikTok posting."""
        # Must be completed
        if self.status != InstanceTaskStatus.COMPLETED:
            return False
        
        # Must have video output
        if not self.get_video_url():
            return False
        
        # Must not already be posted or in progress
        if self.tiktok_post_status in ['PROCESSING', 'PUBLISHED']:
            return False
        
        return True
    
    def update_tiktok_status(self, status: str, publish_id: str = None, post_url: str = None, error: str = None):
        """Update TikTok posting status and related fields."""
        self.tiktok_post_status = status
        
        if publish_id:
            self.tiktok_publish_id = publish_id
        
        if post_url:
            self.tiktok_post_url = post_url
        
        if error and not self.tiktok_post_data:
            self.tiktok_post_data = {}
        
        if error:
            self.tiktok_post_data['error'] = error
            self.tiktok_post_data['error_timestamp'] = datetime.now(timezone.utc).isoformat()
        
        self.updated_at = datetime.now(timezone.utc)


class InstanceMedia(Base):
    """Media files (images) associated with an instance."""
    __tablename__ = "instance_media"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    instance_id = Column(UUID(as_uuid=True), ForeignKey("instances.id", ondelete="CASCADE"), nullable=False)
    
    # File information
    filename = Column(String(255), nullable=False)
    file_type = Column(String(50), nullable=False)  # image/jpeg, image/png, etc.
    storage_path = Column(String(500), nullable=False)  # Path in Supabase storage
    public_url = Column(String(500))  # Public URL if available
    
    # Categorization
    media_category = Column(String(50), default="reference")  # reference, generated, etc.
    
    # Timestamps
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), nullable=False)
    
    # Relationships
    instance = relationship("Instance", back_populates="media")
    
    # Indexes
    __table_args__ = (
        Index('idx_instance_media_instance', 'instance_id'),
    )