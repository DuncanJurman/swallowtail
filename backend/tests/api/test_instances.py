"""Tests for instance API endpoints."""

import uuid
from unittest.mock import Mock, patch
import pytest
from fastapi.testclient import TestClient

from src.api.main import app
from src.models.instance import Instance, InstanceType, InstanceTask, InstanceTaskStatus
from src.models.instance_schemas import InstanceResponse, InstanceTaskResponse


client = TestClient(app)


class TestInstanceAPI:
    """Test cases for instance API endpoints."""
    
    @pytest.fixture
    def mock_db(self):
        """Mock database session."""
        with patch("src.api.instances.get_db") as mock:
            yield mock
    
    @pytest.fixture
    def mock_user_id(self):
        """Mock current user ID."""
        user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
        with patch("src.api.instances.get_current_user_id", return_value=user_id):
            yield user_id
    
    @pytest.fixture
    def mock_instance(self):
        """Create a mock instance."""
        instance = Mock(spec=Instance)
        instance.id = uuid.uuid4()
        instance.user_id = uuid.UUID("00000000-0000-0000-0000-000000000001")
        instance.name = "Test Store"
        instance.type = InstanceType.ECOMMERCE
        instance.business_profile = {"industry": "fashion"}
        instance.configuration = {"max_concurrent_tasks": 3}
        instance.created_at = "2024-01-01T00:00:00"
        instance.updated_at = "2024-01-01T00:00:00"
        return instance
    
    def test_create_instance(self, mock_db, mock_user_id, mock_instance):
        """Test creating a new instance."""
        # Arrange
        mock_service = Mock()
        mock_service.create_instance.return_value = mock_instance
        
        with patch("src.api.instances.InstanceService", return_value=mock_service):
            # Act
            response = client.post(
                "/api/v1/instances/",
                json={
                    "name": "Test Store",
                    "type": "ecommerce",
                    "business_profile": {"industry": "fashion"}
                }
            )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Store"
        assert data["type"] == "ecommerce"
        assert data["business_profile"]["industry"] == "fashion"
    
    def test_list_instances(self, mock_db, mock_user_id, mock_instance):
        """Test listing user's instances."""
        # Arrange
        mock_service = Mock()
        mock_service.list_instances.return_value = [mock_instance, mock_instance]
        
        with patch("src.api.instances.InstanceService", return_value=mock_service):
            # Act
            response = client.get("/api/v1/instances/")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Test Store"
    
    def test_get_instance_success(self, mock_db, mock_user_id, mock_instance):
        """Test getting a specific instance."""
        # Arrange
        mock_service = Mock()
        mock_service.get_instance.return_value = mock_instance
        
        with patch("src.api.instances.InstanceService", return_value=mock_service):
            # Act
            response = client.get(f"/api/v1/instances/{mock_instance.id}")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == str(mock_instance.id)
        assert data["name"] == "Test Store"
    
    def test_get_instance_not_found(self, mock_db, mock_user_id):
        """Test getting non-existent instance."""
        # Arrange
        mock_service = Mock()
        mock_service.get_instance.return_value = None
        
        with patch("src.api.instances.InstanceService", return_value=mock_service):
            # Act
            response = client.get(f"/api/v1/instances/{uuid.uuid4()}")
        
        # Assert
        assert response.status_code == 404
        assert response.json()["detail"] == "Instance not found"
    
    def test_update_instance(self, mock_db, mock_user_id, mock_instance):
        """Test updating instance properties."""
        # Arrange
        updated_instance = Mock(spec=Instance)
        updated_instance.id = mock_instance.id
        updated_instance.user_id = mock_instance.user_id
        updated_instance.name = "Updated Store"
        updated_instance.type = mock_instance.type
        updated_instance.business_profile = {"industry": "tech"}
        updated_instance.configuration = mock_instance.configuration
        updated_instance.created_at = mock_instance.created_at
        updated_instance.updated_at = "2024-01-02T00:00:00"
        
        mock_service = Mock()
        mock_service.update_instance.return_value = updated_instance
        
        with patch("src.api.instances.InstanceService", return_value=mock_service):
            # Act
            response = client.patch(
                f"/api/v1/instances/{mock_instance.id}",
                json={
                    "name": "Updated Store",
                    "business_profile": {"industry": "tech"}
                }
            )
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Store"
        assert data["business_profile"]["industry"] == "tech"
    
    def test_submit_task(self, mock_db, mock_user_id):
        """Test submitting a task to an instance."""
        # Arrange
        instance_id = uuid.uuid4()
        task = Mock(spec=InstanceTask)
        task.id = uuid.uuid4()
        task.instance_id = instance_id
        task.description = "Create product listing"
        task.status = InstanceTaskStatus.QUEUED
        task.execution_plan = None
        task.result_data = None
        task.error_message = None
        task.created_at = "2024-01-01T00:00:00"
        task.started_at = None
        task.completed_at = None
        
        mock_service = Mock()
        mock_service.submit_task.return_value = task
        
        with patch("src.api.instances.InstanceService", return_value=mock_service):
            # Act
            response = client.post(
                f"/api/v1/instances/{instance_id}/tasks",
                json={
                    "description": "Create product listing",
                    "attached_media_ids": []
                }
            )
        
        # Assert
        assert response.status_code == 201
        data = response.json()
        assert data["description"] == "Create product listing"
        assert data["status"] == "queued"
    
    def test_list_tasks(self, mock_db, mock_user_id):
        """Test listing tasks for an instance."""
        # Arrange
        instance_id = uuid.uuid4()
        task1 = Mock(spec=InstanceTask)
        task1.id = uuid.uuid4()
        task1.instance_id = instance_id
        task1.description = "Task 1"
        task1.status = InstanceTaskStatus.COMPLETED
        task1.execution_plan = {}
        task1.result_data = {"success": True}
        task1.error_message = None
        task1.created_at = "2024-01-01T00:00:00"
        task1.started_at = "2024-01-01T00:01:00"
        task1.completed_at = "2024-01-01T00:02:00"
        
        task2 = Mock(spec=InstanceTask)
        task2.id = uuid.uuid4()
        task2.instance_id = instance_id
        task2.description = "Task 2"
        task2.status = InstanceTaskStatus.IN_PROGRESS
        task2.execution_plan = {}
        task2.result_data = None
        task2.error_message = None
        task2.created_at = "2024-01-01T00:03:00"
        task2.started_at = "2024-01-01T00:04:00"
        task2.completed_at = None
        
        mock_service = Mock()
        mock_service.get_instance_tasks.return_value = [task1, task2]
        
        with patch("src.api.instances.InstanceService", return_value=mock_service):
            # Act
            response = client.get(f"/api/v1/instances/{instance_id}/tasks")
        
        # Assert
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["description"] == "Task 1"
        assert data[0]["status"] == "completed"
        assert data[1]["description"] == "Task 2"
        assert data[1]["status"] == "in_progress"