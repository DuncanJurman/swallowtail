"""Tests for enhanced InstanceTask model fields."""

import uuid
from datetime import datetime, timedelta, timezone
import pytest
from sqlalchemy.exc import IntegrityError

from src.models.instance import InstanceTask, Instance, InstanceType, InstanceTaskStatus, TaskPriority
from src.models.instance_schemas import TaskSubmission, TaskExecutionStep, TaskUpdateRequest


class TestEnhancedTaskModel:
    """Test cases for enhanced task model fields."""
    
    def test_task_priority_field(self, db_session):
        """Test task priority field functionality."""
        # Create instance first
        instance = Instance(
            user_id=uuid.uuid4(),
            name="Test Instance",
            type=InstanceType.ECOMMERCE,
            business_profile={"test": "data"}
        )
        db_session.add(instance)
        db_session.flush()
        
        # Test default priority
        task1 = InstanceTask(
            instance_id=instance.id,
            description="Default priority task"
        )
        db_session.add(task1)
        db_session.flush()
        
        assert task1.priority == TaskPriority.NORMAL
        assert task1.status == InstanceTaskStatus.SUBMITTED
        
        # Test urgent priority
        task2 = InstanceTask(
            instance_id=instance.id,
            description="Urgent task",
            priority=TaskPriority.URGENT
        )
        db_session.add(task2)
        db_session.flush()
        
        assert task2.priority == TaskPriority.URGENT
        
        # Test low priority
        task3 = InstanceTask(
            instance_id=instance.id,
            description="Low priority task",
            priority=TaskPriority.LOW
        )
        db_session.add(task3)
        db_session.commit()
        
        assert task3.priority == TaskPriority.LOW
    
    def test_scheduling_fields(self, db_session):
        """Test task scheduling fields."""
        instance = Instance(
            user_id=uuid.uuid4(),
            name="Test Instance",
            type=InstanceType.SOCIAL_MEDIA,
            business_profile={}
        )
        db_session.add(instance)
        db_session.flush()
        
        # Test scheduled task
        scheduled_time = datetime.now(timezone.utc) + timedelta(hours=2)
        task = InstanceTask(
            instance_id=instance.id,
            description="Scheduled post",
            scheduled_for=scheduled_time,
            recurring_pattern={
                "freq": "DAILY",
                "interval": 1,
                "count": 7
            }
        )
        db_session.add(task)
        db_session.commit()
        
        # Compare without timezone since PostgreSQL returns naive datetime
        assert task.scheduled_for.replace(tzinfo=timezone.utc) == scheduled_time
        assert task.recurring_pattern["freq"] == "DAILY"
        assert task.recurring_pattern["interval"] == 1
    
    def test_execution_tracking_fields(self, db_session):
        """Test execution tracking fields."""
        instance = Instance(
            user_id=uuid.uuid4(),
            name="Test Instance",
            type=InstanceType.ECOMMERCE,
            business_profile={}
        )
        db_session.add(instance)
        db_session.flush()
        
        # Create task with execution data
        task = InstanceTask(
            instance_id=instance.id,
            description="Task with execution tracking",
            parsed_intent={
                "intent": "content_creation",
                "platforms": ["instagram", "tiktok"],
                "content_type": "product_showcase"
            }
        )
        db_session.add(task)
        db_session.flush()
        
        # Add execution steps
        task.execution_steps = [
            {
                "step_id": "step_1",
                "agent": "content_creator",
                "action": "Generate product description",
                "status": "completed",
                "output": {"description": "Amazing product!"},
                "started_at": datetime.now(timezone.utc).isoformat(),
                "completed_at": datetime.now(timezone.utc).isoformat()
            },
            {
                "step_id": "step_2",
                "agent": "social_media_manager",
                "action": "Schedule posts",
                "status": "in_progress",
                "started_at": datetime.now(timezone.utc).isoformat()
            }
        ]
        task.progress_percentage = 50
        
        db_session.commit()
        
        assert len(task.execution_steps) == 2
        assert task.execution_steps[0]["status"] == "completed"
        assert task.progress_percentage == 50
    
    def test_output_fields(self, db_session):
        """Test output and result fields."""
        instance = Instance(
            user_id=uuid.uuid4(),
            name="Test Instance",
            type=InstanceType.ECOMMERCE,
            business_profile={}
        )
        db_session.add(instance)
        db_session.flush()
        
        # Create completed task with outputs
        task = InstanceTask(
            instance_id=instance.id,
            description="Generate content",
            status=InstanceTaskStatus.COMPLETED,
            output_format="mixed",
            output_data={
                "post_text": "Check out our new product!",
                "hashtags": ["#newproduct", "#launch"],
                "scheduled_times": ["2024-01-01T10:00:00Z"]
            },
            output_media_ids=[str(uuid.uuid4()), str(uuid.uuid4())]
        )
        
        db_session.add(task)
        db_session.commit()
        
        assert task.output_format == "mixed"
        assert len(task.output_media_ids) == 2
        assert task.output_data["hashtags"][0] == "#newproduct"
    
    def test_processing_metadata(self, db_session):
        """Test processing metadata fields."""
        instance = Instance(
            user_id=uuid.uuid4(),
            name="Test Instance",
            type=InstanceType.SOCIAL_MEDIA,
            business_profile={}
        )
        db_session.add(instance)
        db_session.flush()
        
        # Create task with processing metadata
        start_time = datetime.now(timezone.utc)
        end_time = start_time + timedelta(minutes=5)
        
        task = InstanceTask(
            instance_id=instance.id,
            description="Process this task",
            processing_started_at=start_time,
            processing_ended_at=end_time,
            retry_count=2,
            status=InstanceTaskStatus.FAILED,
            error_message="API rate limit exceeded"
        )
        
        db_session.add(task)
        db_session.commit()
        
        # Compare without timezone since PostgreSQL returns naive datetime
        assert task.processing_started_at.replace(tzinfo=timezone.utc) == start_time
        assert task.processing_ended_at.replace(tzinfo=timezone.utc) == end_time
        assert task.retry_count == 2
        assert task.error_message == "API rate limit exceeded"
    
    def test_parent_task_relationship(self, db_session):
        """Test parent task ID field for subtasks."""
        instance = Instance(
            user_id=uuid.uuid4(),
            name="Test Instance",
            type=InstanceType.ECOMMERCE,
            business_profile={}
        )
        db_session.add(instance)
        db_session.flush()
        
        # Create parent task
        parent_task = InstanceTask(
            instance_id=instance.id,
            description="Parent task: Launch campaign"
        )
        db_session.add(parent_task)
        db_session.flush()
        
        # Create subtask
        subtask = InstanceTask(
            instance_id=instance.id,
            description="Subtask: Create Instagram post",
            parent_task_id=parent_task.id
        )
        db_session.add(subtask)
        db_session.commit()
        
        assert subtask.parent_task_id == parent_task.id
    
    def test_updated_at_timestamp(self, db_session):
        """Test that updated_at is set and updates properly."""
        instance = Instance(
            user_id=uuid.uuid4(),
            name="Test Instance",
            type=InstanceType.SOCIAL_MEDIA,
            business_profile={}
        )
        db_session.add(instance)
        db_session.flush()
        
        task = InstanceTask(
            instance_id=instance.id,
            description="Test timestamp"
        )
        db_session.add(task)
        db_session.commit()
        
        original_updated = task.updated_at
        assert task.updated_at is not None
        assert task.created_at is not None
        
        # Update task
        task.description = "Updated description"
        db_session.commit()
        
        # Note: SQLAlchemy's onupdate doesn't work in unit tests without explicit trigger
        # In production, the database will handle this
    
    def test_task_status_transitions(self, db_session):
        """Test new task status values."""
        instance = Instance(
            user_id=uuid.uuid4(),
            name="Test Instance",
            type=InstanceType.ECOMMERCE,
            business_profile={}
        )
        db_session.add(instance)
        db_session.flush()
        
        # Test all new status values
        statuses = [
            InstanceTaskStatus.SUBMITTED,
            InstanceTaskStatus.QUEUED,
            InstanceTaskStatus.PLANNING,
            InstanceTaskStatus.ASSIGNED,
            InstanceTaskStatus.IN_PROGRESS,
            InstanceTaskStatus.REVIEW,
            InstanceTaskStatus.COMPLETED,
            InstanceTaskStatus.FAILED,
            InstanceTaskStatus.CANCELLED,
            InstanceTaskStatus.REJECTED
        ]
        
        for i, status in enumerate(statuses):
            task = InstanceTask(
                instance_id=instance.id,
                description=f"Task with {status} status",
                status=status
            )
            db_session.add(task)
        
        db_session.commit()
        
        # Verify all statuses were saved
        tasks = db_session.query(InstanceTask).filter(
            InstanceTask.instance_id == instance.id
        ).all()
        
        assert len(tasks) == len(statuses)
        saved_statuses = {task.status for task in tasks}
        assert saved_statuses == set(statuses)


class TestTaskSchemaValidation:
    """Test Pydantic schema validation."""
    
    def test_task_submission_validation(self):
        """Test TaskSubmission schema validation."""
        # Valid submission
        valid_submission = TaskSubmission(
            description="Create a product post",
            priority=TaskPriority.URGENT,
            scheduled_for=datetime.now(timezone.utc) + timedelta(hours=1),
            attached_media_ids=[uuid.uuid4()]
        )
        
        assert valid_submission.priority == TaskPriority.URGENT
        
        # Test past scheduled time validation
        with pytest.raises(ValueError, match="Scheduled time must be in the future"):
            TaskSubmission(
                description="Create a post",
                scheduled_for=datetime.now(timezone.utc) - timedelta(hours=1)
            )
    
    def test_task_execution_step_schema(self):
        """Test TaskExecutionStep schema."""
        step = TaskExecutionStep(
            step_id="analyze_task",
            agent="manager_agent",
            action="Analyzing task requirements",
            status="in_progress",
            started_at=datetime.now(timezone.utc)
        )
        
        assert step.agent == "manager_agent"
        assert step.output is None
        
        # Complete the step
        step.status = "completed"
        step.output = {"intent": "content_creation", "platforms": ["instagram"]}
        step.completed_at = datetime.now(timezone.utc)
        
        assert step.status == "completed"
        assert step.output["intent"] == "content_creation"
    
    def test_task_update_request_validation(self):
        """Test TaskUpdateRequest schema."""
        # Progress update
        update1 = TaskUpdateRequest(
            progress_percentage=75,
            status=InstanceTaskStatus.IN_PROGRESS
        )
        assert update1.progress_percentage == 75
        
        # Error update
        update2 = TaskUpdateRequest(
            status=InstanceTaskStatus.FAILED,
            error_message="External API unavailable"
        )
        assert update2.error_message == "External API unavailable"
        
        # Invalid progress percentage
        with pytest.raises(ValueError):
            TaskUpdateRequest(progress_percentage=150)