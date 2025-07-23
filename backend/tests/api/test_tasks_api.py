"""Tests for enhanced task API endpoints."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone, timedelta
from uuid import uuid4, UUID
from fastapi.testclient import TestClient

from src.models.instance import Instance, InstanceTask, InstanceTaskStatus, TaskPriority
from src.models.instance_schemas import TaskSubmission, TaskUpdateRequest, TaskListFilters


class TestTaskAPI:
    """Test cases for task API endpoints."""
    
    @pytest.fixture
    def client(self):
        """Create test client."""
        from src.api.main import app
        return TestClient(app)
    
    @pytest.fixture
    def mock_db(self):
        """Create mock database session."""
        return Mock()
    
    @pytest.fixture
    def mock_user_id(self):
        """Mock user ID."""
        return UUID("00000000-0000-0000-0000-000000000001")
    
    @pytest.fixture
    def mock_instance(self, mock_user_id):
        """Create mock instance."""
        instance = Mock(spec=Instance)
        instance.id = uuid4()
        instance.user_id = mock_user_id
        instance.name = "Test Instance"
        return instance
    
    @pytest.fixture
    def mock_task(self, mock_instance):
        """Create mock task."""
        task = Mock(spec=InstanceTask)
        task.id = uuid4()
        task.instance_id = mock_instance.id
        task.description = "Test task"
        task.status = InstanceTaskStatus.SUBMITTED
        task.priority = TaskPriority.NORMAL
        task.created_at = datetime.now(timezone.utc)
        task.execution_steps = []
        return task
    
    @patch('src.api.routes.tasks.get_db')
    @patch('src.api.routes.tasks.TaskQueueService')
    def test_submit_task(self, mock_queue_service, mock_get_db, client, mock_db, mock_instance, mock_task):
        """Test task submission endpoint."""
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = mock_instance
        
        # Mock queue service
        mock_service = Mock()
        mock_queue_service.return_value = mock_service
        mock_service.submit_task.return_value = mock_task
        
        # Make request
        task_data = {
            "description": "Create a product post",
            "priority": "urgent"
        }
        
        response = client.post(
            f"/api/v1/tasks/instances/{mock_instance.id}/tasks",
            json=task_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["id"] == str(mock_task.id)
        assert data["description"] == mock_task.description
        
        # Verify queue service was called
        mock_service.submit_task.assert_called_once()
    
    @patch('src.api.routes.tasks.get_db')
    @patch('src.api.routes.tasks.TaskQueueService')
    def test_list_tasks_with_filters(self, mock_queue_service, mock_get_db, client, mock_db, mock_instance):
        """Test listing tasks with filters."""
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.filter.return_value.first.return_value = mock_instance
        
        # Mock queue service
        mock_service = Mock()
        mock_queue_service.return_value = mock_service
        mock_service.list_tasks.return_value = []
        
        # Make request with filters
        response = client.get(
            f"/api/v1/tasks/instances/{mock_instance.id}/tasks",
            params={
                "status": "completed",
                "priority": "urgent",
                "limit": 10,
                "offset": 0
            }
        )
        
        assert response.status_code == 200
        
        # Verify filters were passed
        mock_service.list_tasks.assert_called_once()
        call_args = mock_service.list_tasks.call_args
        filters = call_args[0][1]
        assert isinstance(filters, TaskListFilters)
        assert filters.status == InstanceTaskStatus.COMPLETED
        assert filters.priority == TaskPriority.URGENT
    
    @patch('src.api.routes.tasks.get_db')
    @patch('src.api.routes.tasks.TaskQueueService')
    def test_get_task_status(self, mock_queue_service, mock_get_db, client, mock_db, mock_task):
        """Test getting task status."""
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = mock_task
        
        # Mock queue service
        mock_service = Mock()
        mock_queue_service.return_value = mock_service
        mock_service.get_task_status.return_value = {
            "task_id": mock_task.id,
            "status": mock_task.status,
            "progress": 50,
            "celery_status": {"state": "PENDING"}
        }
        
        response = client.get(f"/api/v1/tasks/tasks/{mock_task.id}/status")
        
        assert response.status_code == 200
        data = response.json()
        assert data["progress"] == 50
        assert "celery_status" in data
    
    @patch('src.api.routes.tasks.get_db')
    @patch('src.api.routes.tasks.TaskQueueService')
    def test_cancel_task(self, mock_queue_service, mock_get_db, client, mock_db, mock_task):
        """Test cancelling a task."""
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = mock_task
        
        # Mock queue service
        mock_service = Mock()
        mock_queue_service.return_value = mock_service
        mock_service.cancel_task.return_value = True
        
        response = client.post(f"/api/v1/tasks/tasks/{mock_task.id}/cancel")
        
        assert response.status_code == 204
        mock_service.cancel_task.assert_called_once_with(mock_task.id)
    
    @patch('src.api.routes.tasks.get_db')
    @patch('src.api.routes.tasks.TaskQueueService')
    def test_cancel_task_failed(self, mock_queue_service, mock_get_db, client, mock_db, mock_task):
        """Test cancelling a task that cannot be cancelled."""
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = mock_task
        
        # Mock queue service
        mock_service = Mock()
        mock_queue_service.return_value = mock_service
        mock_service.cancel_task.return_value = False
        
        response = client.post(f"/api/v1/tasks/tasks/{mock_task.id}/cancel")
        
        assert response.status_code == 400
        assert "cannot be cancelled" in response.json()["detail"]
    
    @patch('src.api.routes.tasks.get_db')
    @patch('src.api.routes.tasks.TaskQueueService')
    def test_retry_task(self, mock_queue_service, mock_get_db, client, mock_db, mock_task):
        """Test retrying a failed task."""
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = mock_task
        mock_task.status = InstanceTaskStatus.FAILED
        
        # Mock queue service
        mock_service = Mock()
        mock_queue_service.return_value = mock_service
        mock_service.retry_task.return_value = mock_task
        
        response = client.post(f"/api/v1/tasks/tasks/{mock_task.id}/retry")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(mock_task.id)
        mock_service.retry_task.assert_called_once_with(mock_task.id)
    
    @patch('src.api.routes.tasks.get_db')
    @patch('src.api.routes.tasks.TaskQueueService')
    def test_update_task(self, mock_queue_service, mock_get_db, client, mock_db, mock_task):
        """Test updating task properties."""
        mock_get_db.return_value = mock_db
        mock_db.query.return_value.join.return_value.filter.return_value.first.return_value = mock_task
        
        # Mock queue service
        mock_service = Mock()
        mock_queue_service.return_value = mock_service
        mock_service.update_task.return_value = mock_task
        
        update_data = {
            "priority": "urgent",
            "progress_percentage": 75
        }
        
        response = client.patch(
            f"/api/v1/tasks/tasks/{mock_task.id}",
            json=update_data
        )
        
        assert response.status_code == 200
        
        # Verify update was called
        mock_service.update_task.assert_called_once()
        call_args = mock_service.update_task.call_args
        update_req = call_args[0][1]
        assert isinstance(update_req, TaskUpdateRequest)
        assert update_req.priority == TaskPriority.URGENT
        assert update_req.progress_percentage == 75