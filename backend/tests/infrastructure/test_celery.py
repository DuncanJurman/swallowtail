"""Unit tests for Celery task queue configuration."""
import pytest
from unittest.mock import Mock, patch
from celery import Celery
from celery.result import AsyncResult

from src.core.celery_app import celery_app, create_celery_app
from src.core.tasks import agent_task, background_task


@pytest.mark.unit
class TestCeleryConfiguration:
    """Test Celery application configuration."""
    
    def test_celery_app_creation(self):
        """Test that Celery app is created with correct configuration."""
        app = create_celery_app()
        assert isinstance(app, Celery)
        assert app.main == "swallowtail"
        assert "redis://" in app.conf.broker_url
        assert "redis://" in app.conf.result_backend
    
    def test_celery_config_from_settings(self):
        """Test that Celery configuration uses settings."""
        from src.core.config import get_settings
        settings = get_settings()
        app = create_celery_app()
        
        assert settings.redis_url in app.conf.broker_url
        assert settings.redis_url in app.conf.result_backend
    
    def test_task_serialization_config(self):
        """Test task serialization is configured correctly."""
        app = create_celery_app()
        assert app.conf.task_serializer == "json"
        assert app.conf.result_serializer == "json"
        assert app.conf.accept_content == ["json"]


@pytest.mark.unit
class TestCeleryTasks:
    """Test Celery task definitions and execution."""
    
    @pytest.mark.asyncio
    async def test_agent_task_decorator(self):
        """Test agent_task decorator creates valid Celery task."""
        @agent_task
        def sample_agent_task(agent_name: str, payload: dict):
            return {"agent": agent_name, "result": payload}
        
        assert hasattr(sample_agent_task, "delay")
        assert hasattr(sample_agent_task, "apply_async")
        assert sample_agent_task.name == "agent.sample_agent_task"
    
    def test_background_task_decorator(self):
        """Test background_task decorator creates valid Celery task."""
        @background_task
        def sample_background_task(data: str):
            return f"Processed: {data}"
        
        assert hasattr(sample_background_task, "delay")
        assert hasattr(sample_background_task, "apply_async")
        assert sample_background_task.name == "background.sample_background_task"
    
    @patch("src.core.tasks.celery_app.send_task")
    def test_task_execution_with_mock(self, mock_send_task):
        """Test task execution with mocked Celery."""
        mock_result = Mock(spec=AsyncResult)
        mock_result.id = "test-task-id"
        mock_send_task.return_value = mock_result
        
        @agent_task
        def test_task(param: str):
            return param
        
        result = test_task.delay("test")
        assert result.id == "test-task-id"
        mock_send_task.assert_called_once()


@pytest.mark.unit
class TestCeleryMocked:
    """Test Celery integration with the application."""
    
    def test_celery_health_check(self):
        """Test Celery health check functionality."""
        from src.core.tasks import check_celery_health
        
        # Mock the celery inspection
        with patch("src.core.tasks.celery_app.control.inspect") as mock_inspect:
            mock_inspect.return_value.stats.return_value = {"worker1": {}}
            
            health = check_celery_health()
            assert health["status"] == "healthy"
            assert "workers" in health
    
    @pytest.mark.asyncio
    async def test_agent_task_workflow(self):
        """Test complete agent task workflow."""
        from src.core.tasks import execute_agent_task
        
        with patch("src.core.tasks.celery_app.send_task") as mock_send:
            mock_result = Mock()
            mock_result.id = "workflow-task-id"
            mock_result.get.return_value = {"status": "completed"}
            mock_send.return_value = mock_result
            
            result = await execute_agent_task(
                agent_name="TestAgent",
                method="execute",
                payload={"test": "data"}
            )
            
            assert result["status"] == "completed"
            mock_send.assert_called_once()