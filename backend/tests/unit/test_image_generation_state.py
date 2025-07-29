"""Unit tests for ImageGenerationState model."""
import pytest
import json
from datetime import datetime, timezone
from uuid import UUID, uuid4

from src.flows.models import ImageGenerationState


class TestImageGenerationState:
    """Test cases for ImageGenerationState model."""
    
    @pytest.mark.unit
    def test_state_initialization_with_defaults(self):
        """Test that state initializes with correct default values."""
        state = ImageGenerationState()
        
        # Check defaults
        assert state.product_id is None
        assert state.reference_image_url == ""
        assert state.product_name == ""
        assert state.product_features == []
        assert state.style_requirements == {}
        assert state.attempts == 0
        assert state.max_attempts == 3
        assert state.approval_threshold == 0.85
        assert state.generated_images == []
        assert state.feedback_history == []
        assert state.final_image_url is None
        assert state.final_image_path is None
        assert state.approved is False
        assert state.completed_at is None
        assert state.errors == []
    
    @pytest.mark.unit
    def test_state_initialization_with_values(self):
        """Test state initialization with custom values."""
        product_id = uuid4()
        state = ImageGenerationState(
            product_id=product_id,
            reference_image_url="file:///test/image.jpg",
            product_name="Test Product",
            product_features=["Feature 1", "Feature 2"],
            style_requirements={"background": "white", "lighting": "soft"},
            approval_threshold=0.90,
            max_attempts=5
        )
        
        assert state.product_id == product_id
        assert state.reference_image_url == "file:///test/image.jpg"
        assert state.product_name == "Test Product"
        assert state.product_features == ["Feature 1", "Feature 2"]
        assert state.style_requirements == {"background": "white", "lighting": "soft"}
        assert state.approval_threshold == 0.90
        assert state.max_attempts == 5
    
    @pytest.mark.unit
    def test_state_serialization(self):
        """Test that state can be serialized to JSON."""
        product_id = uuid4()
        state = ImageGenerationState(
            product_id=product_id,
            reference_image_url="file:///test/image.jpg",
            product_name="Test Product"
        )
        
        # Add some data
        state.generated_images.append({
            "attempt": 1,
            "image_path": "/tmp/test.png",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Serialize
        json_str = state.model_dump_json()
        data = json.loads(json_str)
        
        # Check serialization
        assert data["product_id"] == str(product_id)
        assert data["product_name"] == "Test Product"
        assert len(data["generated_images"]) == 1
        assert data["generated_images"][0]["attempt"] == 1
    
    @pytest.mark.unit
    def test_state_deserialization(self):
        """Test that state can be deserialized from JSON."""
        product_id = uuid4()
        data = {
            "product_id": str(product_id),
            "reference_image_url": "file:///test/image.jpg",
            "product_name": "Test Product",
            "product_features": ["Feature 1"],
            "attempts": 2,
            "generated_images": [
                {
                    "attempt": "1",  # Must be string
                    "image_path": "/tmp/test1.png",
                    "timestamp": "2024-01-01T00:00:00Z"
                }
            ]
        }
        
        # Deserialize
        state = ImageGenerationState.model_validate(data)
        
        assert state.product_id == product_id
        assert state.product_name == "Test Product"
        assert state.attempts == 2
        assert len(state.generated_images) == 1
        assert state.generated_images[0]["attempt"] == "1"
    
    @pytest.mark.unit
    def test_add_generated_image(self):
        """Test adding generated images to state."""
        state = ImageGenerationState()
        
        # Add first image
        state.generated_images.append({
            "attempt": "1",
            "image_path": "/tmp/img1.png",
            "storage_url": "https://storage.com/img1.png",
            "prompt": "Test prompt 1",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Add second image
        state.generated_images.append({
            "attempt": "2",
            "image_path": "/tmp/img2.png",
            "storage_url": "https://storage.com/img2.png",
            "prompt": "Test prompt 2",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        assert len(state.generated_images) == 2
        assert state.generated_images[0]["attempt"] == "1"
        assert state.generated_images[1]["attempt"] == "2"
        assert state.generated_images[0]["image_path"] == "/tmp/img1.png"
        assert state.generated_images[1]["image_path"] == "/tmp/img2.png"
    
    @pytest.mark.unit
    def test_add_feedback(self):
        """Test adding feedback to history."""
        state = ImageGenerationState()
        
        # Add feedback
        feedback_entry = {
            "attempt": 1,
            "feedback": ["Increase brightness", "Add more blue tones"],
            "scores": {
                "visual_fidelity": 70,
                "product_accuracy": 85
            },
            "overall_score": 75
        }
        state.feedback_history.append(feedback_entry)
        
        assert len(state.feedback_history) == 1
        assert state.feedback_history[0]["attempt"] == 1
        assert len(state.feedback_history[0]["feedback"]) == 2
        assert state.feedback_history[0]["overall_score"] == 75
    
    @pytest.mark.unit
    def test_increment_attempts(self):
        """Test incrementing attempt counter."""
        state = ImageGenerationState()
        
        assert state.attempts == 0
        
        state.attempts += 1
        assert state.attempts == 1
        
        state.attempts += 1
        assert state.attempts == 2
    
    @pytest.mark.unit
    def test_max_attempts_reached(self):
        """Test checking if max attempts have been reached."""
        state = ImageGenerationState(max_attempts=3)
        
        # Not reached yet
        state.attempts = 2
        assert state.attempts < state.max_attempts
        
        # Exactly at max
        state.attempts = 3
        assert state.attempts >= state.max_attempts
        
        # Exceeded
        state.attempts = 4
        assert state.attempts > state.max_attempts
    
    @pytest.mark.unit
    def test_error_tracking(self):
        """Test adding and tracking errors."""
        state = ImageGenerationState()
        
        # Add first error
        state.errors.append({
            "attempt": 1,
            "error": "API rate limit exceeded",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        # Add second error
        state.errors.append({
            "attempt": 2,
            "error": "Image generation failed: Invalid prompt",
            "timestamp": datetime.now(timezone.utc).isoformat()
        })
        
        assert len(state.errors) == 2
        assert state.errors[0]["error"] == "API rate limit exceeded"
        assert state.errors[1]["attempt"] == 2
        assert "timestamp" in state.errors[0]
        assert "timestamp" in state.errors[1]
    
    @pytest.mark.unit
    def test_json_encoding_with_uuid_and_datetime(self):
        """Test that UUID and datetime fields are properly encoded."""
        product_id = uuid4()
        completed_at = datetime.now(timezone.utc)
        
        state = ImageGenerationState(
            product_id=product_id,
            completed_at=completed_at
        )
        
        # Test JSON encoding
        json_str = state.model_dump_json()
        data = json.loads(json_str)
        
        # UUID should be string
        assert isinstance(data["product_id"], str)
        assert data["product_id"] == str(product_id)
        
        # Datetime should be ISO format string
        assert isinstance(data["completed_at"], str)
        assert data["completed_at"] == completed_at.isoformat()
    
    @pytest.mark.unit
    def test_state_completion(self):
        """Test marking state as completed."""
        state = ImageGenerationState()
        
        # Initially not completed
        assert state.approved is False
        assert state.completed_at is None
        assert state.final_image_url is None
        
        # Mark as completed
        state.approved = True
        state.completed_at = datetime.now(timezone.utc)
        state.final_image_url = "https://storage.com/final.png"
        state.final_image_path = "/tmp/final.png"
        
        assert state.approved is True
        assert state.completed_at is not None
        assert state.final_image_url == "https://storage.com/final.png"
        assert state.final_image_path == "/tmp/final.png"
    
    @pytest.mark.unit
    def test_state_with_style_requirements(self):
        """Test state with style requirements (Dict[str, str])."""
        # Style requirements must be Dict[str, str] per the model
        style_requirements = {
            "background": "gradient from black to blue",
            "lighting": "blue LED glow with soft ambient",
            "composition": "center placement at 45 degree angle",
            "atmosphere": "cozy nighttime ambiance"
        }
        
        state = ImageGenerationState(style_requirements=style_requirements)
        
        # Verify structure is preserved
        assert state.style_requirements["background"] == "gradient from black to blue"
        assert state.style_requirements["lighting"] == "blue LED glow with soft ambient"
        assert state.style_requirements["composition"] == "center placement at 45 degree angle"
        assert state.style_requirements["atmosphere"] == "cozy nighttime ambiance"
        
        # Verify serialization works
        json_str = state.model_dump_json()
        data = json.loads(json_str)
        assert data["style_requirements"]["background"] == "gradient from black to blue"
        assert len(data["style_requirements"]) == 4