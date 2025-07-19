"""Pytest configuration and fixtures for comprehensive testing."""
import pytest
import os
import sys
from pathlib import Path
from unittest.mock import Mock, AsyncMock, MagicMock
from uuid import uuid4
import tempfile
from typing import Dict, Any, List
import base64
from PIL import Image
import io

# Add backend directory to Python path
backend_dir = Path(__file__).parent.parent
sys.path.insert(0, str(backend_dir))

from src.flows.models import ImageGenerationState
from src.services.openai_image_service import GenerationResult, EvaluationResult

def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as unit test (no external dependencies)"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as integration test (mocked services)"
    )
    config.addinivalue_line(
        "markers", "e2e: mark test as end-to-end test (requires API keys)"
    )
    config.addinivalue_line(
        "markers", "performance: mark test as performance test"
    )


# Image Fixtures
@pytest.fixture
def sample_image_bytes():
    """Generate sample image data for testing."""
    img = Image.new('RGB', (1024, 1024), color=(0, 100, 200))
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    buffer.seek(0)
    return buffer.read()


@pytest.fixture
def led_squirtle_image():
    """Load actual LED Squirtle reference image."""
    image_path = Path(__file__).parent / "reference_images" / "led-squirtle.jpg"
    if image_path.exists():
        with open(image_path, 'rb') as f:
            return f.read()
    else:
        # Return a mock image if the actual file doesn't exist
        return sample_image_bytes()


@pytest.fixture
def temp_image_path(sample_image_bytes):
    """Create a temporary image file for testing."""
    with tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False) as f:
        f.write(sample_image_bytes)
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


# OpenAI Mock Fixtures
@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client with predictable responses."""
    mock_client = AsyncMock()
    
    # Mock image generation response
    mock_image_response = MagicMock()
    mock_image_response.data = [
        MagicMock(b64_json=base64.b64encode(b"mock_image_data").decode('utf-8'))
    ]
    mock_client.images.edit.return_value = mock_image_response
    
    # Mock chat completion for evaluation
    mock_eval_response = MagicMock()
    mock_parsed = MagicMock(
        overall_score=85,
        visual_fidelity_score=90,
        prompt_accuracy_score=85,
        technical_quality_score=80,
        product_accuracy_score=85,
        issues=[],
        improvements=["Enhance blue lighting effect", "Add more ambient glow"]
    )
    mock_eval_response.choices = [
        MagicMock(message=MagicMock(parsed=mock_parsed))
    ]
    mock_client.chat.completions.parse.return_value = mock_eval_response
    
    return mock_client


@pytest.fixture
def mock_image_generation_response(sample_image_bytes):
    """Mock successful image generation response."""
    return GenerationResult(
        image_data=sample_image_bytes,
        prompt="A LED Squirtle night light in a modern dorm room with blue LED glow"
    )


@pytest.fixture
def mock_image_evaluation_response():
    """Mock image evaluation response with scores."""
    return EvaluationResult(
        approved=True,
        score=0.85,
        feedback=["Great ambient lighting", "Product clearly visible"],
        metadata={
            'visual_fidelity_score': 90,
            'prompt_accuracy_score': 85,
            'technical_quality_score': 80,
            'product_accuracy_score': 85,
            'issues': []
        }
    )


# Crew Mock Fixtures
@pytest.fixture
def mock_crew_execution():
    """Mock successful crew execution."""
    def _mock_execution(success=True, output="", **kwargs):
        if success:
            output = output or """
            Successfully generated image using the generate_image tool.
            temp_image_path: /tmp/generated_12345.png
            The image has been stored successfully.
            url: https://storage.example.com/image.png
            
            Evaluation Results:
            Overall Score: 85/100
            Visual Fidelity: 90/100
            Product Accuracy: 85/100
            Technical Quality: 80/100
            Professional Appearance: 85/100
            E-commerce Suitability: 85/100
            
            Decision: APPROVED
            
            The generated image successfully captures the LED Squirtle in a dorm room 
            setting with blue ambient lighting as requested.
            """
        else:
            output = "Generation failed: API error"
            
        return {
            "success": success,
            "output": output,
            "temp_image_path": "/tmp/generated_12345.png" if success else None,
            "storage_url": "https://storage.example.com/image.png" if success else None,
            **kwargs
        }
    return _mock_execution


@pytest.fixture
def mock_flow_state():
    """Create a mock flow state for testing."""
    state = ImageGenerationState(
        product_id=uuid4(),
        reference_image_url="file:///path/to/reference.jpg",
        product_name="LED Squirtle Night Light",
        product_features=["Blue LED", "Pokemon design", "USB powered"],
        style_requirements={"lighting": "blue ambient", "setting": "dorm room"},
        approval_threshold=0.85
    )
    return state


# Async Fixtures
# Removed custom event_loop fixture - pytest-asyncio handles this automatically


# Cleanup Fixtures
@pytest.fixture
def temp_file_cleanup():
    """Ensure temporary files are cleaned up after tests."""
    temp_files = []
    
    def register(filepath):
        temp_files.append(filepath)
        return filepath
    
    yield register
    
    # Cleanup
    for filepath in temp_files:
        if os.path.exists(filepath):
            os.unlink(filepath)


# API Test Fixtures
@pytest.fixture
def test_client():
    """Create a test client for FastAPI app."""
    from fastapi.testclient import TestClient
    from src.api.main import app
    
    return TestClient(app)


@pytest.fixture
def api_headers():
    """Common headers for API requests."""
    return {
        "Content-Type": "application/json",
        "Accept": "application/json"
    }


# Product Test Data
@pytest.fixture
def led_squirtle_product():
    """LED Squirtle product test data."""
    return {
        "product_id": str(uuid4()),
        "product_name": "LED Squirtle Night Light",
        "product_features": [
            "Blue LED illumination that creates ambient lighting",
            "Squirtle Pokemon character design",
            "Perfect size for dorm room nightstand",
            "Soft glow suitable for nighttime use"
        ],
        "style_requirements": {
            "background": "modern dorm room setting",
            "lighting": "blue LED glow illuminating the room",
            "atmosphere": "cozy nighttime ambiance with the blue light as primary light source",
            "composition": "place on a nightstand or desk in a dorm room"
        },
        "reference_image_url": "file:///tests/reference_images/led-squirtle.jpg",
        "approval_threshold": 0.85
    }


@pytest.fixture
def test_products():
    """Multiple products for batch testing."""
    return [
        {
            "product_id": str(uuid4()),
            "product_name": "Wireless Gaming Mouse",
            "product_features": ["RGB lighting", "Ergonomic design", "7 buttons"],
            "reference_image_url": "file:///tests/reference_images/gaming_mouse.jpg"
        },
        {
            "product_id": str(uuid4()),
            "product_name": "Mechanical Keyboard",
            "product_features": ["Cherry MX switches", "Backlit keys", "Compact"],
            "reference_image_url": "file:///tests/reference_images/keyboard.jpg"
        }
    ]


# Performance Testing Fixtures
@pytest.fixture
def performance_timer():
    """Timer for performance testing."""
    import time
    
    class Timer:
        def __init__(self):
            self.start_time = None
            self.elapsed = None
            
        def __enter__(self):
            self.start_time = time.time()
            return self
            
        def __exit__(self, *args):
            self.elapsed = time.time() - self.start_time
            
    return Timer


# Environment Setup
@pytest.fixture(scope="session", autouse=True)
def setup_test_env():
    """Setup test environment variables."""
    os.environ["ENVIRONMENT"] = "test"
    os.environ["REDIS_URL"] = "redis://localhost:6379/4"  # Test DB
    yield
    # Cleanup if needed