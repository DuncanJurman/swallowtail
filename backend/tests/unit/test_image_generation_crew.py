"""Unit tests for ImageGenerationCrew."""
import pytest
from unittest.mock import Mock, patch, MagicMock, AsyncMock
from uuid import uuid4

from src.crews.image_generation_crew import ImageGenerationCrew
from src.core.config import get_settings


class TestImageGenerationCrew:
    """Test cases for ImageGenerationCrew."""
    
    @pytest.mark.unit
    def test_crew_initialization(self):
        """Test crew initialization with required parameters."""
        product_id = uuid4()
        crew = ImageGenerationCrew(
            product_id=product_id,
            reference_image_url="file:///test/reference.jpg",
            product_name="Test Product",
            product_features=["Feature 1", "Feature 2"],
            style_requirements={"background": "white", "lighting": "soft"}
        )
        
        assert crew.product_id == product_id
        assert crew.reference_image_url == "file:///test/reference.jpg"
        assert crew.product_name == "Test Product"
        assert crew.product_features == ["Feature 1", "Feature 2"]
        assert crew.style_requirements == {"background": "white", "lighting": "soft"}
        assert crew.previous_feedback == []
        assert crew.generation_tool is not None
        assert crew.storage_tool is not None
    
    @pytest.mark.unit
    def test_crew_initialization_with_feedback(self):
        """Test crew initialization with previous feedback."""
        feedback = [
            {"attempt": "1", "feedback": "Increase brightness"},
            {"attempt": "2", "feedback": "Adjust color balance"}
        ]
        
        crew = ImageGenerationCrew(
            product_id=uuid4(),
            reference_image_url="file:///test/reference.jpg",
            product_name="Test Product",
            product_features=["Feature 1"],
            previous_feedback=feedback
        )
        
        assert crew.previous_feedback == feedback
        assert len(crew.previous_feedback) == 2
    
    @pytest.mark.unit
    @patch('src.crews.image_generation_crew.LLM')
    def test_agent_creation_with_multimodal(self, mock_llm):
        """Test that image generator agent is created with multimodal capabilities."""
        crew = ImageGenerationCrew(
            product_id=uuid4(),
            reference_image_url="file:///test/reference.jpg",
            product_name="Test Product",
            product_features=["Feature 1"]
        )
        
        # Get the agent
        agent = crew.image_generator()
        
        # Verify agent configuration
        assert agent.multimodal is True
        assert len(agent.tools) == 2  # generation_tool and storage_tool
        assert agent.verbose is True
        
        # Verify LLM was configured
        mock_llm.assert_called_once()
        llm_args = mock_llm.call_args[1]
        assert llm_args['model'] == get_settings().openai_model
        assert llm_args['temperature'] == 0.7
        assert llm_args['max_tokens'] == 4000
    
    @pytest.mark.unit
    def test_task_creation_without_feedback(self):
        """Test task creation when no previous feedback exists."""
        crew = ImageGenerationCrew(
            product_id=uuid4(),
            reference_image_url="file:///test/reference.jpg",
            product_name="LED Light",
            product_features=["Blue LED", "USB Powered"],
            style_requirements={"background": "dark", "lighting": "dramatic"}
        )
        
        task = crew.generate_image_task()
        
        # Check task description contains key elements
        assert "LED Light" in task.description
        assert "file:///test/reference.jpg" in task.description
        assert "Blue LED" in task.description
        assert "USB Powered" in task.description
        assert "Background: dark" in task.description
        assert "Lighting: dramatic" in task.description
        assert "PREVIOUS FEEDBACK" not in task.description
        
        # Check expected output
        assert "successfully generated" in task.expected_output
        assert "URL of the stored image" in task.expected_output
    
    @pytest.mark.unit
    def test_task_creation_with_feedback(self):
        """Test task creation with previous feedback incorporated."""
        feedback = [
            {"attempt": "1", "feedback": "Increase blue lighting intensity"},
            {"attempt": "2", "feedback": "Add more ambient glow"}
        ]
        
        crew = ImageGenerationCrew(
            product_id=uuid4(),
            reference_image_url="file:///test/reference.jpg",
            product_name="LED Light",
            product_features=["Blue LED"],
            previous_feedback=feedback
        )
        
        task = crew.generate_image_task()
        
        # Check feedback is included
        assert "PREVIOUS FEEDBACK TO ADDRESS:" in task.description
        assert "Attempt 1: Increase blue lighting intensity" in task.description
        assert "Attempt 2: Add more ambient glow" in task.description
        assert "Consider the previous feedback" in task.description
    
    @pytest.mark.unit
    def test_tools_assignment(self):
        """Test that correct tools are assigned to the agent."""
        crew = ImageGenerationCrew(
            product_id=uuid4(),
            reference_image_url="file:///test/reference.jpg",
            product_name="Test Product",
            product_features=["Feature 1"]
        )
        
        agent = crew.image_generator()
        tool_names = [tool.name for tool in agent.tools]
        
        assert len(agent.tools) == 2
        assert "generate_image" in tool_names
        assert "store_image" in tool_names
    
    @pytest.mark.unit
    @patch('src.crews.image_generation_crew.Crew')
    def test_crew_configuration(self, mock_crew_class):
        """Test crew is configured with correct parameters."""
        crew = ImageGenerationCrew(
            product_id=uuid4(),
            reference_image_url="file:///test/reference.jpg",
            product_name="Test Product",
            product_features=["Feature 1"]
        )
        
        # Call crew method
        crew_instance = crew.crew()
        
        # Verify Crew was created with correct parameters
        mock_crew_class.assert_called_once()
        crew_args = mock_crew_class.call_args[1]
        
        assert crew_args['process'].value == "sequential"
        assert crew_args['verbose'] is True
        assert crew_args['memory'] is True
        assert crew_args['planning'] is True
        assert 'planning_llm' in crew_args
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.crews.image_generation_crew.ImageGenerationCrew.crew')
    async def test_execute_async_success(self, mock_crew, mock_crew_execution):
        """Test successful async execution of the crew."""
        # Setup mock crew
        mock_crew_instance = Mock()
        mock_crew.return_value = mock_crew_instance
        
        # Mock successful execution result
        mock_result = Mock()
        mock_result.raw = mock_crew_execution(success=True)["output"]
        mock_crew_instance.kickoff.return_value = mock_result
        
        crew = ImageGenerationCrew(
            product_id=uuid4(),
            reference_image_url="file:///test/reference.jpg",
            product_name="Test Product",
            product_features=["Feature 1"]
        )
        
        result = await crew.execute_async()
        
        assert result["success"] is True
        assert "output" in result
        assert "product_id" in result
        assert result["temp_image_path"] == "/tmp/generated_12345.png"
        assert result["storage_url"] == "https://storage.example.com/image.png"
        
        # Verify kickoff was called with correct inputs
        mock_crew_instance.kickoff.assert_called_once()
        kickoff_args = mock_crew_instance.kickoff.call_args[1]["inputs"]
        assert kickoff_args["product_name"] == "Test Product"
        assert kickoff_args["reference_image_url"] == "file:///test/reference.jpg"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    @patch('src.crews.image_generation_crew.ImageGenerationCrew.crew')
    async def test_execute_async_failure(self, mock_crew):
        """Test handling of execution failure."""
        # Setup mock crew to raise exception
        mock_crew_instance = Mock()
        mock_crew.return_value = mock_crew_instance
        mock_crew_instance.kickoff.side_effect = Exception("API Error")
        
        crew = ImageGenerationCrew(
            product_id=uuid4(),
            reference_image_url="file:///test/reference.jpg",
            product_name="Test Product",
            product_features=["Feature 1"]
        )
        
        result = await crew.execute_async()
        
        assert result["success"] is False
        assert result["error"] == "API Error"
        assert "product_id" in result
    
    @pytest.mark.unit
    def test_output_parsing(self):
        """Test parsing of crew execution output."""
        crew = ImageGenerationCrew(
            product_id=uuid4(),
            reference_image_url="file:///test/reference.jpg",
            product_name="Test Product",
            product_features=["Feature 1"]
        )
        
        # Test output with path extraction
        test_output = """
        Successfully generated image.
        temp_image_path: /tmp/test_image_123.png
        The image has been stored.
        url: https://storage.example.com/final_image.png
        """
        
        # Simulate the regex parsing logic from execute_async
        import re
        
        path_match = re.search(r'temp_image_path["\s:]+([^\s",]+)', test_output)
        assert path_match is not None
        assert path_match.group(1) == "/tmp/test_image_123.png"
        
        url_match = re.search(r'url["\s:]+([^\s",]+)', test_output)
        assert url_match is not None
        assert url_match.group(1) == "https://storage.example.com/final_image.png"
    
    @pytest.mark.unit
    def test_prepare_crew_hook(self):
        """Test the before_kickoff prepare_crew method."""
        crew = ImageGenerationCrew(
            product_id=uuid4(),
            reference_image_url="file:///test/reference.jpg",
            product_name="Test Product",
            product_features=["Feature 1"]
        )
        
        inputs = {"test": "data"}
        updated_inputs = crew.prepare_crew(inputs)
        
        assert "timestamp" in updated_inputs
        assert "test" in updated_inputs
        assert updated_inputs["test"] == "data"
        
        # Verify timestamp is in ISO format
        from datetime import datetime
        timestamp = datetime.fromisoformat(updated_inputs["timestamp"])
        assert timestamp is not None