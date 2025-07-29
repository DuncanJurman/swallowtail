"""Tests for image generation workflow."""

import pytest
from unittest.mock import AsyncMock, patch

from src.workflows.image_generation_workflow import ImageGenerationWorkflow
from src.agents.base import AgentResult


@pytest.fixture
def workflow():
    """Create workflow instance for testing."""
    return ImageGenerationWorkflow(max_attempts=3)


@pytest.fixture
def mock_image_data():
    """Mock image data."""
    return b"fake_image_data"


@pytest.fixture
def mock_reference_url():
    """Mock reference URL."""
    return "https://example.com/reference.png"


@pytest.mark.asyncio
async def test_successful_image_generation_first_attempt(workflow, mock_image_data, mock_reference_url):
    """Test successful image generation on first attempt."""
    # Mock generation agent response
    gen_result = AgentResult(
        success=True,
        data={
            'image_data': mock_image_data,
            'prompt': 'Professional product photography',
            'product_name': 'Test Product'
        }
    )
    
    # Mock evaluation agent response (approved)
    eval_result = AgentResult(
        success=True,
        data={
            'approved': True,
            'score': 0.9,
            'feedback': []
        }
    )
    
    # Mock storage response
    mock_storage_url = "https://storage.example.com/product.png"
    
    # Patch the agent methods
    with patch.object(workflow.generation_agent, 'execute', AsyncMock(return_value=gen_result)):
        with patch.object(workflow.evaluator_agent, 'execute', AsyncMock(return_value=eval_result)):
            with patch.object(workflow.storage, 'upload_image', AsyncMock(return_value=mock_storage_url)):
                
                result = await workflow.generate_product_image(
                    product_id="test-123",
                    reference_image_url=mock_reference_url,
                    product_name="Test Product",
                    product_features=["Feature 1", "Feature 2"],
                    approval_threshold=0.85
                )
    
    assert result['success'] is True
    assert result['image_url'] == mock_storage_url
    assert result['score'] == 0.9
    assert result['attempts'] == 1


@pytest.mark.asyncio
async def test_image_generation_with_regeneration(workflow, mock_image_data, mock_reference_url):
    """Test image generation that requires regeneration."""
    # First generation result
    gen_result1 = AgentResult(
        success=True,
        data={
            'image_data': mock_image_data,
            'prompt': 'Initial prompt',
            'product_name': 'Test Product'
        }
    )
    
    # First evaluation (not approved)
    eval_result1 = AgentResult(
        success=True,
        data={
            'approved': False,
            'score': 0.7,
            'feedback': ['Improve lighting', 'Show product features more clearly']
        }
    )
    
    # Second generation result
    gen_result2 = AgentResult(
        success=True,
        data={
            'image_data': mock_image_data,
            'prompt': 'Enhanced prompt with feedback',
            'product_name': 'Test Product'
        }
    )
    
    # Second evaluation (approved)
    eval_result2 = AgentResult(
        success=True,
        data={
            'approved': True,
            'score': 0.88,
            'feedback': []
        }
    )
    
    mock_storage_url = "https://storage.example.com/product_v2.png"
    
    # Mock the sequence of calls
    workflow.generation_agent.execute = AsyncMock(side_effect=[gen_result1, gen_result2])
    workflow.evaluator_agent.execute = AsyncMock(side_effect=[eval_result1, eval_result2])
    workflow.storage.upload_image = AsyncMock(return_value=mock_storage_url)
    
    result = await workflow.generate_product_image(
        product_id="test-456",
        reference_image_url=mock_reference_url,
        product_name="Test Product",
        product_features=["Feature 1", "Feature 2"],
        approval_threshold=0.85
    )
    
    assert result['success'] is True
    assert result['attempts'] == 2
    assert result['score'] == 0.88


@pytest.mark.asyncio
async def test_max_attempts_reached(workflow, mock_image_data, mock_reference_url):
    """Test when max attempts are reached without approval."""
    # All generations succeed but evaluations fail
    gen_result = AgentResult(
        success=True,
        data={
            'image_data': mock_image_data,
            'prompt': 'Test prompt',
            'product_name': 'Test Product'
        }
    )
    
    eval_result = AgentResult(
        success=True,
        data={
            'approved': False,
            'score': 0.6,
            'feedback': ['Quality too low']
        }
    )
    
    workflow.generation_agent.execute = AsyncMock(return_value=gen_result)
    workflow.evaluator_agent.execute = AsyncMock(return_value=eval_result)
    
    result = await workflow.generate_product_image(
        product_id="test-789",
        reference_image_url=mock_reference_url,
        product_name="Test Product",
        product_features=["Feature 1"],
        approval_threshold=0.85
    )
    
    assert result['success'] is False
    assert result['attempts'] == 3
    assert 'Failed to generate approved image' in result['error']


@pytest.mark.asyncio
async def test_generation_error_handling(workflow, mock_reference_url):
    """Test error handling when generation fails."""
    # Generation fails
    gen_error = AgentResult(
        success=False,
        error="API error: rate limit exceeded"
    )
    
    workflow.generation_agent.execute = AsyncMock(return_value=gen_error)
    
    # Set max_attempts on workflow instance
    workflow.max_attempts = 1
    
    result = await workflow.generate_product_image(
        product_id="test-error",
        reference_image_url=mock_reference_url,
        product_name="Test Product",
        product_features=["Feature 1"]
    )
    
    # Even with generation failure, workflow completes
    assert result['success'] is False
    assert result['attempts'] == 1