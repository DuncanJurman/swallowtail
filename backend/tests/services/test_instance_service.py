"""Tests for InstanceService."""

import uuid
from datetime import datetime
from unittest.mock import Mock, MagicMock
import pytest

from src.services.instance_service import InstanceService
from src.models.instance import Instance, InstanceAgent, InstanceTask, InstanceType, InstanceTaskStatus
from src.models.instance_schemas import InstanceCreate, TaskSubmission


class TestInstanceService:
    """Test cases for InstanceService."""
    
    @pytest.fixture
    def mock_db(self):
        """Create a mock database session."""
        db = Mock()
        db.add = Mock()
        db.commit = Mock()
        db.refresh = Mock()
        db.flush = Mock()
        db.query = Mock()
        return db
    
    @pytest.fixture
    def service(self, mock_db):
        """Create an InstanceService with mock database."""
        return InstanceService(mock_db)
    
    @pytest.fixture
    def user_id(self):
        """Generate a test user ID."""
        return uuid.uuid4()
    
    @pytest.fixture
    def instance_id(self):
        """Generate a test instance ID."""
        return uuid.uuid4()
    
    def test_create_instance_ecommerce(self, service, mock_db, user_id):
        """Test creating an e-commerce instance."""
        # Arrange
        instance_data = InstanceCreate(
            name="Test Store",
            type=InstanceType.ECOMMERCE,
            business_profile={"industry": "fashion", "target_audience": "millennials"}
        )
        
        # Act
        result = service.create_instance(user_id, instance_data)
        
        # Assert
        mock_db.add.assert_called()
        mock_db.flush.assert_called_once()
        mock_db.commit.assert_called_once()
        
        # Verify instance was created with correct attributes
        created_instance = mock_db.add.call_args_list[0][0][0]
        assert isinstance(created_instance, Instance)
        assert created_instance.user_id == user_id
        assert created_instance.name == "Test Store"
        assert created_instance.type == InstanceType.ECOMMERCE
        assert created_instance.business_profile == {"industry": "fashion", "target_audience": "millennials"}
        
        # Verify default configuration
        assert created_instance.configuration["max_concurrent_tasks"] == 3
        assert created_instance.configuration["enable_product_generation"] is True
        assert "shopify" in created_instance.configuration["platforms"]
        
        # Verify agents were created (4 total: 1 instance + 3 agents)
        assert mock_db.add.call_count == 4
        
        # Check manager agent
        manager_agent = mock_db.add.call_args_list[1][0][0]
        assert isinstance(manager_agent, InstanceAgent)
        assert manager_agent.agent_type == "manager"
        assert manager_agent.is_enabled is True
        
        # Check product creator agent
        product_agent = mock_db.add.call_args_list[2][0][0]
        assert product_agent.agent_type == "product_creator"
        
        # Check market analyst agent
        analyst_agent = mock_db.add.call_args_list[3][0][0]
        assert analyst_agent.agent_type == "market_analyst"
    
    def test_create_instance_social_media(self, service, mock_db, user_id):
        """Test creating a social media instance."""
        # Arrange
        instance_data = InstanceCreate(
            name="Brand Social",
            type=InstanceType.SOCIAL_MEDIA,
            business_profile={"industry": "fitness", "tone": "motivational"}
        )
        
        # Act
        result = service.create_instance(user_id, instance_data)
        
        # Assert
        created_instance = mock_db.add.call_args_list[0][0][0]
        assert created_instance.type == InstanceType.SOCIAL_MEDIA
        assert created_instance.configuration["enable_content_scheduling"] is True
        assert "instagram" in created_instance.configuration["platforms"]
        
        # Verify social media specific agents
        content_agent = mock_db.add.call_args_list[2][0][0]
        assert content_agent.agent_type == "content_creator"
        
        social_agent = mock_db.add.call_args_list[3][0][0]
        assert social_agent.agent_type == "social_manager"
    
    def test_get_instance_success(self, service, mock_db, user_id, instance_id):
        """Test successfully getting an instance."""
        # Arrange
        mock_instance = Mock(spec=Instance)
        mock_instance.id = instance_id
        mock_instance.user_id = user_id
        
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = mock_instance
        mock_db.query.return_value = mock_query
        
        # Act
        result = service.get_instance(instance_id, user_id)
        
        # Assert
        assert result == mock_instance
        mock_db.query.assert_called_with(Instance)
    
    def test_get_instance_wrong_user(self, service, mock_db, user_id, instance_id):
        """Test getting instance fails for wrong user."""
        # Arrange
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.first.return_value = None
        mock_db.query.return_value = mock_query
        
        # Act
        result = service.get_instance(instance_id, uuid.uuid4())  # Different user
        
        # Assert
        assert result is None
    
    def test_list_instances(self, service, mock_db, user_id):
        """Test listing user's instances."""
        # Arrange
        mock_instances = [Mock(spec=Instance), Mock(spec=Instance)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_instances
        mock_db.query.return_value = mock_query
        
        # Act
        result = service.list_instances(user_id)
        
        # Assert
        assert result == mock_instances
        assert len(result) == 2
    
    def test_update_instance(self, service, mock_db, user_id, instance_id):
        """Test updating instance properties."""
        # Arrange
        mock_instance = Mock(spec=Instance)
        mock_instance.id = instance_id
        mock_instance.user_id = user_id
        mock_instance.name = "Old Name"
        mock_instance.business_profile = {"old": "profile"}
        
        # Mock get_instance to return our instance
        service.get_instance = Mock(return_value=mock_instance)
        
        updates = {
            "name": "New Name",
            "business_profile": {"new": "profile", "industry": "tech"},
            "invalid_field": "should be ignored"
        }
        
        # Act
        result = service.update_instance(instance_id, user_id, updates)
        
        # Assert
        assert result == mock_instance
        assert mock_instance.name == "New Name"
        assert mock_instance.business_profile == {"new": "profile", "industry": "tech"}
        mock_db.commit.assert_called_once()
        mock_db.refresh.assert_called_once_with(mock_instance)
    
    def test_submit_task_success(self, service, mock_db, user_id, instance_id):
        """Test submitting a task."""
        # Arrange
        mock_instance = Mock(spec=Instance)
        service.get_instance = Mock(return_value=mock_instance)
        
        task_data = TaskSubmission(
            description="Create a product listing for summer collection",
            attached_media_ids=[uuid.uuid4(), uuid.uuid4()]
        )
        
        # Act
        result = service.submit_task(instance_id, user_id, task_data)
        
        # Assert
        mock_db.add.assert_called_once()
        task = mock_db.add.call_args[0][0]
        assert isinstance(task, InstanceTask)
        assert task.instance_id == instance_id
        assert task.description == "Create a product listing for summer collection"
        assert task.status == InstanceTaskStatus.QUEUED
        assert len(task.attached_media_ids) == 2
    
    def test_submit_task_invalid_instance(self, service, mock_db, user_id, instance_id):
        """Test submitting task to non-existent instance."""
        # Arrange
        service.get_instance = Mock(return_value=None)
        task_data = TaskSubmission(description="Test task")
        
        # Act
        result = service.submit_task(instance_id, user_id, task_data)
        
        # Assert
        assert result is None
        mock_db.add.assert_not_called()
    
    def test_get_instance_tasks_with_status(self, service, mock_db, user_id, instance_id):
        """Test getting tasks filtered by status."""
        # Arrange
        mock_instance = Mock(spec=Instance)
        service.get_instance = Mock(return_value=mock_instance)
        
        mock_tasks = [Mock(spec=InstanceTask), Mock(spec=InstanceTask)]
        mock_query = Mock()
        mock_query.filter.return_value = mock_query
        mock_query.order_by.return_value = mock_query
        mock_query.all.return_value = mock_tasks
        mock_db.query.return_value = mock_query
        
        # Act
        result = service.get_instance_tasks(instance_id, user_id, InstanceTaskStatus.COMPLETED)
        
        # Assert
        assert result == mock_tasks
        # Verify status filter was applied
        filter_calls = mock_query.filter.call_args_list
        assert len(filter_calls) == 2  # instance_id and status