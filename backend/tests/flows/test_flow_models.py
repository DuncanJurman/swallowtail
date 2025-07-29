"""Test flow models."""

from uuid import uuid4, UUID
from datetime import datetime, timezone
from src.flows.models import ImageGenerationState


def test_image_generation_state_creation():
    """Test creating an ImageGenerationState."""
    state = ImageGenerationState(
        product_id=uuid4(),
        reference_image_url="https://example.com/ref.jpg",
        product_name="Test Product",
        product_features=["Feature 1", "Feature 2"],
        style_requirements={"background": "white", "lighting": "soft"}
    )
    
    assert state.attempts == 0
    assert state.max_attempts == 3
    assert state.approval_threshold == 0.85
    assert not state.approved
    assert state.final_image_url is None
    assert len(state.generated_images) == 0
    assert len(state.feedback_history) == 0
    assert len(state.errors) == 0


def test_image_generation_state_update():
    """Test updating ImageGenerationState."""
    state = ImageGenerationState(
        product_id=uuid4(),
        reference_image_url="https://example.com/ref.jpg",
        product_name="Test Product"
    )
    
    # Add generated image
    state.generated_images.append({
        "attempt": 1,
        "image_path": "/tmp/image1.png",
        "prompt": "Test prompt",
        "timestamp": datetime.now(timezone.utc).isoformat()
    })
    state.attempts += 1
    
    assert state.attempts == 1
    assert len(state.generated_images) == 1
    assert state.generated_images[0]["attempt"] == 1
    
    # Add feedback
    state.feedback_history.append({
        "attempt": 1,
        "feedback": "Needs better lighting",
        "scores": {"quality": 75, "accuracy": 80}
    })
    
    assert len(state.feedback_history) == 1
    assert state.feedback_history[0]["feedback"] == "Needs better lighting"
    
    # Mark as approved
    state.approved = True
    state.final_image_url = "https://storage.example.com/final.png"
    state.completed_at = datetime.now(timezone.utc)
    
    assert state.approved
    assert state.final_image_url is not None
    assert state.completed_at is not None


def test_image_generation_state_serialization():
    """Test serializing ImageGenerationState to dict."""
    state = ImageGenerationState(
        product_id=uuid4(),
        reference_image_url="https://example.com/ref.jpg",
        product_name="Test Product"
    )
    
    # Convert to dict
    state_dict = state.model_dump()
    
    assert isinstance(state_dict["product_id"], UUID)  # UUID stays as UUID in dict
    assert state_dict["reference_image_url"] == "https://example.com/ref.jpg"
    assert state_dict["product_name"] == "Test Product"
    assert state_dict["attempts"] == 0
    
    # Convert to JSON string to test serialization
    import json
    state_json = state.model_dump_json()
    state_from_json = json.loads(state_json)
    assert isinstance(state_from_json["product_id"], str)  # UUID serialized to string in JSON


if __name__ == "__main__":
    test_image_generation_state_creation()
    test_image_generation_state_update()
    test_image_generation_state_serialization()
    print("✅ All model tests passed!")