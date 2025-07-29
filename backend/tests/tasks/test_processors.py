"""Tests for task processors."""

import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timezone
from uuid import uuid4

from src.tasks.processors.default_processor import DefaultTaskProcessor
from src.tasks.processors.content_creation_processor import ContentCreationProcessor
from src.models.instance import InstanceTask, InstanceTaskStatus


class TestDefaultTaskProcessor:
    """Test cases for DefaultTaskProcessor."""
    
    @pytest.fixture
    def mock_task(self):
        """Create a mock task."""
        task = Mock(spec=InstanceTask)
        task.id = uuid4()
        task.instance_id = uuid4()
        task.description = "Test default task"
        task.execution_steps = []
        task.parsed_intent = None
        return task
    
    @pytest.fixture
    def processor(self, mock_task):
        """Create a processor with mocked context."""
        processor = DefaultTaskProcessor(mock_task.id, mock_task.instance_id)
        processor.task = mock_task
        processor.db_session = Mock()
        processor.task_id = mock_task.id
        processor.instance_id = mock_task.instance_id
        return processor
    
    def test_process_success(self, processor, mock_task):
        """Test successful task processing."""
        with patch.object(processor, 'update_progress') as mock_progress:
            with patch.object(processor, 'add_execution_step') as mock_add_step:
                with patch.object(processor, 'set_output') as mock_set_output:
                    with patch('time.sleep'):  # Skip sleep in tests
                        result = processor.process()
        
        # Verify result
        assert result['status'] == 'success'
        assert 'result' in result
        assert result['result']['processor'] == 'DefaultTaskProcessor'
        
        # Verify progress updates
        progress_calls = mock_progress.call_args_list
        assert len(progress_calls) >= 4
        assert progress_calls[-1][0][0] == 100  # Final progress percentage
        
        # Verify execution steps added
        assert mock_add_step.call_count >= 2
        
        # Verify output set
        mock_set_output.assert_called_once()
        output_kwargs = mock_set_output.call_args[1]
        assert output_kwargs['output_format'] == 'json'
        assert 'message' in output_kwargs['output_data']
    
    def test_parse_intent_called(self, processor, mock_task):
        """Test that parse_intent is called during processing."""
        with patch.object(processor, 'parse_intent') as mock_parse:
            mock_parse.return_value = {"intent_type": "test"}
            with patch.object(processor, 'update_progress'):
                with patch.object(processor, 'add_execution_step'):
                    with patch.object(processor, 'set_output'):
                        with patch('time.sleep'):
                            processor.process()
        
        mock_parse.assert_called_once()
        assert mock_task.parsed_intent == {"intent_type": "test"}


class TestContentCreationProcessor:
    """Test cases for ContentCreationProcessor."""
    
    @pytest.fixture
    def mock_task(self):
        """Create a mock task for content creation."""
        task = Mock(spec=InstanceTask)
        task.id = uuid4()
        task.instance_id = uuid4()
        task.description = "Create Instagram and TikTok posts about our new product launch"
        task.execution_steps = []
        return task
    
    @pytest.fixture
    def processor(self, mock_task):
        """Create a processor with mocked context."""
        processor = ContentCreationProcessor(mock_task.id, mock_task.instance_id)
        processor.task = mock_task
        processor.db_session = Mock()
        processor.task_id = mock_task.id
        processor.instance_id = mock_task.instance_id
        return processor
    
    def test_process_content_creation(self, processor, mock_task):
        """Test content creation processing."""
        with patch.object(processor, 'update_progress') as mock_progress:
            with patch.object(processor, 'add_execution_step') as mock_add_step:
                with patch.object(processor, 'set_output') as mock_set_output:
                    with patch('time.sleep'):  # Skip sleep in tests
                        result = processor.process()
        
        # Verify result
        assert result['status'] == 'success'
        assert 'content' in result['result']
        assert 'platforms' in result['result']
        assert 'instagram' in result['result']['platforms']
        assert 'tiktok' in result['result']['platforms']
        
        # Verify output was set
        mock_set_output.assert_called_once()
        output_kwargs = mock_set_output.call_args[1]
        output_data = output_kwargs['output_data']
        
        assert 'content' in output_data
        assert 'instagram' in output_data['content']
        assert 'tiktok' in output_data['content']
        assert output_data['content_type'] == 'product_showcase'
    
    def test_extract_platforms(self, processor):
        """Test platform extraction from description."""
        test_cases = [
            ("Post on Instagram and Facebook", ["instagram", "facebook"]),
            ("Create TikTok video", ["tiktok"]),
            ("Share on LinkedIn", ["linkedin"]),
            ("Tweet about it", ["twitter"]),
            ("Upload to YouTube", ["youtube"]),
            ("General post", ["instagram"]),  # Default
        ]
        
        for description, expected_platforms in test_cases:
            platforms = processor._extract_platforms(description)
            assert set(platforms) == set(expected_platforms)
    
    def test_determine_content_type(self, processor):
        """Test content type determination."""
        test_cases = [
            ("Showcase our new product", "product_showcase"),
            ("Share our brand story", "brand_story"),
            ("Announce the launch", "announcement"),
            ("Tips on how to use", "educational"),
            ("Random content", "general_post"),
        ]
        
        for description, expected_type in test_cases:
            content_type = processor._determine_content_type(description)
            assert content_type == expected_type
    
    def test_generate_dummy_content(self, processor):
        """Test dummy content generation."""
        content = processor._generate_dummy_content("product_showcase", ["instagram"])
        
        assert 'title' in content
        assert 'body' in content
        assert 'cta' in content
        assert '#' in content['body']  # Has hashtags
    
    def test_optimize_for_platforms(self, processor):
        """Test platform optimization."""
        content = {
            "title": "Test Title",
            "body": "Test body #test #hashtag",
            "cta": "Test CTA"
        }
        
        optimized = processor._optimize_for_platforms(content, ["instagram", "twitter"])
        
        # Check Instagram optimization
        assert 'instagram' in optimized
        assert optimized['instagram']['type'] == 'feed_post'
        assert '#test' in optimized['instagram']['hashtags']
        
        # Check Twitter optimization
        assert 'twitter' in optimized
        assert optimized['twitter']['type'] == 'tweet'
        assert 'thread' in optimized['twitter']
        assert len(optimized['twitter']['hashtags']) <= 3  # Twitter limit
    
    def test_extract_hashtags(self, processor):
        """Test hashtag extraction."""
        text = "Check out our #NewProduct! #Launch #Innovation #Quality"
        hashtags = processor._extract_hashtags(text)
        
        assert len(hashtags) == 4
        assert '#NewProduct' in hashtags
        assert '#Launch' in hashtags
    
    def test_estimate_reach(self, processor):
        """Test reach estimation."""
        reach = processor._estimate_reach(["instagram", "tiktok", "facebook"])
        assert reach == 18000  # 5000 + 10000 + 3000
        
        reach = processor._estimate_reach(["unknown_platform"])
        assert reach == 1000  # Default
    
    def test_media_generation_for_visual_content(self, processor, mock_task):
        """Test that media is generated for visual content types."""
        mock_task.description = "Create product showcase for Instagram"
        
        with patch.object(processor, 'update_progress'):
            with patch.object(processor, 'add_execution_step'):
                with patch.object(processor, 'set_output') as mock_set_output:
                    with patch('time.sleep'):
                        with patch('uuid.uuid4', return_value='mock-uuid'):
                            result = processor.process()
        
        # Verify media was generated
        output_kwargs = mock_set_output.call_args[1]
        assert output_kwargs['output_format'] == 'mixed'  # output_format when media present
        assert len(output_kwargs['output_media_ids']) == 2  # output_media_ids
    
    def test_execution_steps_added(self, processor, mock_task):
        """Test that all execution steps are properly added."""
        step_count = 0
        
        def count_steps(*args):
            nonlocal step_count
            step_count += 1
        
        with patch.object(processor, 'update_progress'):
            with patch.object(processor, 'add_execution_step', side_effect=count_steps):
                with patch.object(processor, 'set_output'):
                    with patch('time.sleep'):
                        processor.process()
        
        # Should have at least 4 steps (analyze, generate, optimize, media)
        assert step_count >= 4