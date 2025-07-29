"""Tests for task queue service."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
from uuid import uuid4

from src.tasks.queue_service import TaskQueueService
from src.tasks.processors.default_processor import DefaultTaskProcessor
from src.tasks.processors.content_creation_processor import ContentCreationProcessor
from src.models.instance import Instance, InstanceTask, InstanceTaskStatus, TaskPriority
from src.models.instance_schemas import TaskSubmission, TaskUpdateRequest, TaskListFilters


class TestTaskQueueService:
    """Test cases for TaskQueueService."""
    
    @pytest.fixture
    def mock_db_session(self):
        """Create a mock database session."""
        return Mock()
    
    @pytest.fixture
    def mock_instance(self):
        """Create a mock instance."""
        instance = Mock(spec=Instance)
        instance.id = uuid4()
        instance.name = "Test Instance"
        return instance
    
    @pytest.fixture
    def mock_task(self, mock_instance):
        """Create a mock task."""
        task = Mock(spec=InstanceTask)
        task.id = uuid4()
        task.instance_id = mock_instance.id
        task.description = "Test task description"
        task.status = InstanceTaskStatus.SUBMITTED
        task.priority = TaskPriority.NORMAL
        task.execution_steps = []
        task.created_at = datetime.now(timezone.utc)
        return task
    
    @pytest.fixture
    def service(self, mock_db_session):
        """Create a TaskQueueService instance."""
        service = TaskQueueService(mock_db_session)
        # Register test processors
        TaskQueueService.register_processor('default', DefaultTaskProcessor)
        TaskQueueService.register_processor('content_creation', ContentCreationProcessor)
        return service
    
    def test_register_processor(self):
        """Test processor registration."""
        TaskQueueService._processor_registry = {}  # Reset registry
        
        TaskQueueService.register_processor('test', DefaultTaskProcessor)
        assert 'test' in TaskQueueService._processor_registry
        assert TaskQueueService._processor_registry['test'] == DefaultTaskProcessor
    
    def test_submit_task_success(self, service, mock_db_session, mock_instance):
        """Test successful task submission."""
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_instance
        
        submission = TaskSubmission(
            description="Create a social media post",
            priority=TaskPriority.URGENT
        )
        
        with patch.object(service, '_queue_task') as mock_queue:
            task = service.submit_task(mock_instance.id, submission)
            
            # Verify task was created
            mock_db_session.add.assert_called_once()
            mock_db_session.commit.assert_called()
            
            # Verify task was queued (no schedule)
            mock_queue.assert_called_once()
            
            # Verify task attributes
            added_task = mock_db_session.add.call_args[0][0]
            assert added_task.description == submission.description
            assert added_task.priority == submission.priority
            assert added_task.status == InstanceTaskStatus.SUBMITTED
    
    def test_submit_task_scheduled(self, service, mock_db_session, mock_instance):
        """Test scheduled task submission."""
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_instance
        
        future_time = datetime.now(timezone.utc) + timedelta(hours=2)
        submission = TaskSubmission(
            description="Scheduled post",
            scheduled_for=future_time
        )
        
        with patch.object(service, '_queue_task') as mock_queue:
            task = service.submit_task(mock_instance.id, submission)
            
            # Verify task was not queued immediately
            mock_queue.assert_not_called()
    
    def test_submit_task_instance_not_found(self, service, mock_db_session):
        """Test task submission with invalid instance."""
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        submission = TaskSubmission(description="Test")
        
        with pytest.raises(ValueError, match="Instance .* not found"):
            service.submit_task(uuid4(), submission)
    
    @patch('src.tasks.queue_service.celery_app')
    def test_queue_task_with_processor(self, mock_celery, service, mock_db_session, mock_task):
        """Test queuing task with matched processor."""
        mock_task.description = "Create social media content"
        
        service._queue_task(mock_task)
        
        # Verify task status updated
        assert mock_task.status == InstanceTaskStatus.QUEUED
        assert mock_task.parsed_intent is not None
        assert mock_task.parsed_intent['intent_type'] == 'content_creation'
        
        # Verify Celery task sent
        mock_celery.send_task.assert_called_once()
        call_args = mock_celery.send_task.call_args
        assert call_args[0][0] == 'process_task'
        assert call_args[1]['queue'] == 'default'  # Normal priority
        assert call_args[1]['task_id'] == f"task_{mock_task.id}"
    
    @patch('src.tasks.queue_service.celery_app')
    def test_queue_task_urgent_priority(self, mock_celery, service, mock_db_session, mock_task):
        """Test urgent tasks go to high priority queue."""
        mock_task.priority = TaskPriority.URGENT
        
        service._queue_task(mock_task)
        
        call_args = mock_celery.send_task.call_args
        assert call_args[1]['queue'] == 'agents'  # High priority queue
    
    def test_queue_task_no_processor(self, service, mock_db_session, mock_task):
        """Test queuing task with no matching processor."""
        # Clear registry to ensure no processors
        TaskQueueService._processor_registry = {}
        
        service._queue_task(mock_task)
        
        assert mock_task.status == InstanceTaskStatus.FAILED
        assert "No processor available" in mock_task.error_message
        mock_db_session.commit.assert_called()
    
    def test_parse_intent_type(self, service):
        """Test intent type parsing."""
        assert service._parse_intent_type("Create a social media post") == "content_creation"
        assert service._parse_intent_type("Analyze market trends") == "market_analysis"
        assert service._parse_intent_type("Send email campaign") == "email_campaign"
        assert service._parse_intent_type("Update product listing") == "product_management"
        assert service._parse_intent_type("Random task") == "general"
    
    def test_get_queue_name(self, service):
        """Test queue name determination."""
        assert service._get_queue_name(TaskPriority.URGENT) == "agents"
        assert service._get_queue_name(TaskPriority.NORMAL) == "default"
        assert service._get_queue_name(TaskPriority.LOW) == "background"
    
    @patch('src.tasks.queue_service.AsyncResult')
    def test_get_task_status(self, mock_async_result, service, mock_db_session, mock_task):
        """Test getting task status."""
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_task
        mock_task.status = InstanceTaskStatus.IN_PROGRESS
        
        # Mock Celery result
        mock_result = Mock()
        mock_result.state = "PENDING"
        mock_result.info = {"progress": 50}
        mock_async_result.return_value = mock_result
        
        status = service.get_task_status(mock_task.id)
        
        assert status['task_id'] == mock_task.id
        assert status['status'] == InstanceTaskStatus.IN_PROGRESS
        assert status['celery_status']['state'] == "PENDING"
        assert status['celery_status']['info']['progress'] == 50
    
    def test_update_task(self, service, mock_db_session, mock_task):
        """Test updating task."""
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_task
        
        update = TaskUpdateRequest(
            status=InstanceTaskStatus.IN_PROGRESS,
            progress_percentage=75,
            error_message="Test error"
        )
        
        updated_task = service.update_task(mock_task.id, update)
        
        assert mock_task.status == InstanceTaskStatus.IN_PROGRESS
        assert mock_task.progress_percentage == 75
        assert mock_task.error_message == "Test error"
        mock_db_session.commit.assert_called()
    
    @patch('src.tasks.queue_service.celery_app')
    def test_cancel_task(self, mock_celery, service, mock_db_session, mock_task):
        """Test task cancellation."""
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_task
        mock_task.status = InstanceTaskStatus.IN_PROGRESS
        
        result = service.cancel_task(mock_task.id)
        
        assert result is True
        assert mock_task.status == InstanceTaskStatus.CANCELLED
        assert mock_task.processing_ended_at is not None
        
        # Verify Celery revoke called
        mock_celery.control.revoke.assert_called_once_with(
            f"task_{mock_task.id}",
            terminate=True
        )
    
    def test_cancel_completed_task(self, service, mock_db_session, mock_task):
        """Test cannot cancel completed task."""
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_task
        mock_task.status = InstanceTaskStatus.COMPLETED
        
        result = service.cancel_task(mock_task.id)
        
        assert result is False
        assert mock_task.status == InstanceTaskStatus.COMPLETED
    
    def test_retry_task(self, service, mock_db_session, mock_task):
        """Test retrying failed task."""
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_task
        mock_task.status = InstanceTaskStatus.FAILED
        mock_task.retry_count = 1
        
        with patch.object(service, '_queue_task') as mock_queue:
            retried_task = service.retry_task(mock_task.id)
            
            assert mock_task.status == InstanceTaskStatus.SUBMITTED
            assert mock_task.error_message is None
            assert mock_task.retry_count == 2
            mock_queue.assert_called_once_with(mock_task)
    
    def test_retry_non_failed_task(self, service, mock_db_session, mock_task):
        """Test cannot retry non-failed task."""
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = mock_task
        mock_task.status = InstanceTaskStatus.IN_PROGRESS
        
        with pytest.raises(ValueError, match="Can only retry failed tasks"):
            service.retry_task(mock_task.id)
    
    def test_list_tasks(self, service, mock_db_session, mock_instance):
        """Test listing tasks with filters."""
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter_by.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.limit.return_value = mock_query
        mock_query.offset.return_value = mock_query
        mock_query.all.return_value = []
        
        filters = TaskListFilters(
            status=InstanceTaskStatus.COMPLETED,
            priority=TaskPriority.URGENT,
            limit=10,
            offset=0
        )
        
        tasks = service.list_tasks(mock_instance.id, filters)
        
        # Verify query construction
        mock_query.filter_by.assert_called_with(instance_id=mock_instance.id)
        mock_query.limit.assert_called_with(10)
        mock_query.offset.assert_called_with(0)
    
    def test_process_scheduled_tasks(self, service, mock_db_session):
        """Test processing scheduled tasks."""
        # Create mock scheduled tasks
        mock_tasks = [Mock(spec=InstanceTask) for _ in range(3)]
        for task in mock_tasks:
            task.status = InstanceTaskStatus.SUBMITTED
            
        mock_query = Mock()
        mock_db_session.query.return_value = mock_query
        mock_query.filter.return_value = mock_query
        mock_query.all.return_value = mock_tasks
        
        with patch.object(service, '_queue_task') as mock_queue:
            count = service.process_scheduled_tasks()
            
            assert count == 3
            assert mock_queue.call_count == 3
            mock_db_session.commit.assert_called()