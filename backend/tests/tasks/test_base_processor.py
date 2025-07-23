"""Tests for base task processor."""

import pytest
from unittest.mock import Mock, patch
from datetime import datetime, timezone
from uuid import uuid4

from src.tasks.base_processor import BaseTaskProcessor
from src.models.instance import InstanceTask, InstanceTaskStatus
from src.models.instance_schemas import TaskExecutionStep


class ConcreteTaskProcessor(BaseTaskProcessor):
    """Concrete implementation for testing."""
    
    def process(self):
        return {"status": "processed"}


class TestBaseTaskProcessor:
    """Test cases for BaseTaskProcessor."""
    
    @pytest.fixture
    def mock_task(self):
        """Create a mock task."""
        task = Mock(spec=InstanceTask)
        task.id = uuid4()
        task.instance_id = uuid4()
        task.description = "Test task"
        task.status = InstanceTaskStatus.SUBMITTED
        task.execution_steps = []
        task.progress_percentage = 0
        return task
    
    @pytest.fixture
    def mock_db_session(self, mock_task):
        """Create a mock database session."""
        session = Mock()
        session.query.return_value.filter_by.return_value.first.return_value = mock_task
        return session
    
    def test_context_manager_initialization(self, mock_db_session, mock_task):
        """Test processor initialization via context manager."""
        task_id = mock_task.id
        instance_id = mock_task.instance_id
        
        with patch('src.tasks.base_processor.get_session', return_value=iter([mock_db_session])):
            with ConcreteTaskProcessor(task_id, instance_id) as processor:
                assert processor.task_id == task_id
                assert processor.instance_id == instance_id
                assert processor.task == mock_task
                assert processor.db_session == mock_db_session
    
    def test_context_manager_task_not_found(self, mock_db_session):
        """Test error when task not found."""
        mock_db_session.query.return_value.filter_by.return_value.first.return_value = None
        
        with patch('src.tasks.base_processor.get_session', return_value=iter([mock_db_session])):
            with pytest.raises(ValueError, match="Task .* not found"):
                with ConcreteTaskProcessor(uuid4(), uuid4()) as processor:
                    pass
    
    def test_update_status(self, mock_db_session, mock_task):
        """Test status update functionality."""
        with patch('src.tasks.base_processor.get_session', return_value=iter([mock_db_session])):
            with ConcreteTaskProcessor(mock_task.id, mock_task.instance_id) as processor:
                # Test status update to IN_PROGRESS
                processor.update_status(InstanceTaskStatus.IN_PROGRESS)
                assert mock_task.status == InstanceTaskStatus.IN_PROGRESS
                assert mock_task.processing_started_at is not None
                
                # Test status update to FAILED with error
                processor.update_status(InstanceTaskStatus.FAILED, "Test error")
                assert mock_task.status == InstanceTaskStatus.FAILED
                assert mock_task.error_message == "Test error"
                assert mock_task.processing_ended_at is not None
                
                mock_db_session.commit.assert_called()
    
    def test_update_progress(self, mock_db_session, mock_task):
        """Test progress update functionality."""
        with patch('src.tasks.base_processor.get_session', return_value=iter([mock_db_session])):
            with ConcreteTaskProcessor(mock_task.id, mock_task.instance_id) as processor:
                # Test basic progress update
                processor.update_progress(50)
                assert mock_task.progress_percentage == 50
                
                # Test progress with message
                processor.update_progress(75, "Processing data")
                assert mock_task.progress_percentage == 75
                assert len(mock_task.execution_steps) == 1
                assert mock_task.execution_steps[0]['action'] == "Processing data"
                
                # Test progress bounds
                processor.update_progress(150)
                assert mock_task.progress_percentage == 100
                
                processor.update_progress(-10)
                assert mock_task.progress_percentage == 0
                
                mock_db_session.commit.assert_called()
    
    def test_add_execution_step(self, mock_db_session, mock_task):
        """Test adding execution steps."""
        with patch('src.tasks.base_processor.get_session', return_value=iter([mock_db_session])):
            with ConcreteTaskProcessor(mock_task.id, mock_task.instance_id) as processor:
                step = TaskExecutionStep(
                    step_id="test_step",
                    agent="TestAgent",
                    action="Testing",
                    status="completed",
                    started_at=datetime.now(timezone.utc),
                    completed_at=datetime.now(timezone.utc),
                    output={"result": "success"}
                )
                
                processor.add_execution_step(step)
                
                assert len(mock_task.execution_steps) == 1
                assert mock_task.execution_steps[0]['step_id'] == "test_step"
                assert mock_task.execution_steps[0]['agent'] == "TestAgent"
                mock_db_session.commit.assert_called()
    
    def test_set_output(self, mock_db_session, mock_task):
        """Test setting task output."""
        with patch('src.tasks.base_processor.get_session', return_value=iter([mock_db_session])):
            with ConcreteTaskProcessor(mock_task.id, mock_task.instance_id) as processor:
                output_data = {"result": "test output"}
                media_ids = [str(uuid4()), str(uuid4())]
                
                processor.set_output("json", output_data, media_ids)
                
                assert mock_task.output_format == "json"
                assert mock_task.output_data == output_data
                assert mock_task.output_media_ids == media_ids
                mock_db_session.commit.assert_called()
    
    def test_parse_intent_default(self, mock_db_session, mock_task):
        """Test default intent parsing."""
        with patch('src.tasks.base_processor.get_session', return_value=iter([mock_db_session])):
            with ConcreteTaskProcessor(mock_task.id, mock_task.instance_id) as processor:
                intent = processor.parse_intent()
                
                assert intent['raw_description'] == "Test task"
                assert intent['intent_type'] == "unknown"
                assert intent['entities'] == []
                assert intent['confidence'] == 0.0
    
    def test_context_manager_rollback_on_error(self, mock_db_session, mock_task):
        """Test that database rolls back on error."""
        with patch('src.tasks.base_processor.get_session', return_value=iter([mock_db_session])):
            try:
                with ConcreteTaskProcessor(mock_task.id, mock_task.instance_id) as processor:
                    raise Exception("Test error")
            except Exception:
                pass
            
            mock_db_session.rollback.assert_called()
            mock_db_session.commit.assert_not_called()
    
    def test_runtime_error_without_context(self):
        """Test runtime errors when not using context manager."""
        processor = ConcreteTaskProcessor(uuid4(), uuid4())
        
        with pytest.raises(RuntimeError, match="Processor not initialized"):
            processor.update_status(InstanceTaskStatus.IN_PROGRESS)
        
        with pytest.raises(RuntimeError, match="Processor not initialized"):
            processor.update_progress(50)
        
        with pytest.raises(RuntimeError, match="Processor not initialized"):
            processor.add_execution_step(Mock())
        
        with pytest.raises(RuntimeError, match="Processor not initialized"):
            processor.set_output("json", {})