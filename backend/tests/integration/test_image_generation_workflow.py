"""
Integration tests for the complete image generation workflow.

These tests verify the end-to-end functionality of:
1. Image generation using OpenAI API
2. Image storage in Supabase
3. Quality evaluation with feedback loops
4. Complete flow orchestration
"""
import os
import pytest
import asyncio
from pathlib import Path
from uuid import uuid4
from dotenv import load_dotenv

# Load environment
load_dotenv()

from src.crews.image_generation_crew import ImageGenerationCrew
from src.flows.image_generation_flow import ImageGenerationFlow
from src.core.config import get_settings


class TestImageGenerationWorkflow:
    """Test the complete image generation workflow with real API calls."""
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for integration testing"
    )
    @pytest.mark.timeout(300)  # 5 minute timeout
    def test_crew_direct_execution(self):
        """Test that ImageGenerationCrew can generate images directly."""
        # Setup
        reference_image_path = Path(__file__).parent.parent / "reference_images" / "led-squirtle.jpg"
        assert reference_image_path.exists(), f"Reference image not found at {reference_image_path}"
        
        # Create crew with specific requirements
        crew = ImageGenerationCrew(
            product_id=uuid4(),
            reference_image_url=f"file://{reference_image_path.absolute()}",
            product_name="LED Squirtle Night Light",
            product_features=[
                "Blue LED illumination that creates ambient lighting",
                "Squirtle Pokemon character design",
                "Perfect size for dorm room nightstand"
            ],
            style_requirements={
                "setting": "modern college dorm room at night",
                "lighting": "blue LED glow illuminating the entire room",
                "placement": "on nightstand next to bed",
                "atmosphere": "cozy nighttime ambiance"
            }
        )
        
        # Execute crew
        print(f"\n🚀 Testing direct crew execution for: {crew.product_name}")
        result = asyncio.run(crew.execute_async())
        
        # Validate results
        assert result["success"], f"Crew execution failed: {result.get('error', 'Unknown error')}"
        assert result.get("temp_image_path"), "No temporary image path returned"
        assert result.get("output"), "No output generated from crew"
        
        # Verify image was actually created
        temp_path = result.get("temp_image_path")
        if temp_path:
            assert os.path.exists(temp_path), f"Generated image not found at {temp_path}"
            file_size = os.path.getsize(temp_path)
            assert file_size > 10000, f"Generated image suspiciously small: {file_size} bytes"
            print(f"✅ Image generated: {temp_path} ({file_size:,} bytes)")
            
            # Save to output directory
            output_dir = Path("output/generated_images")
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Create descriptive filename
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"led_squirtle_dorm_room_{timestamp}.png"
            
            # Copy the image
            import shutil
            shutil.copy2(temp_path, output_path)
            print(f"✅ Image saved to: {output_path}")
            
            # Cleanup temp file
            os.remove(temp_path)
            print("✅ Temporary file cleaned up")
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for integration testing"
    )
    def test_flow_with_single_attempt(self):
        """Test ImageGenerationFlow with approval on first attempt."""
        # Setup
        reference_image_path = Path(__file__).parent.parent / "reference_images" / "led-squirtle.jpg"
        assert reference_image_path.exists()
        
        product_id = uuid4()
        product_info = {
            "name": "LED Squirtle Night Light",
            "features": [
                "Blue LED creates room-filling ambient light",
                "Authentic Squirtle character from Pokemon",
                "USB powered for convenience"
            ],
            "style": {
                "setting": "cozy dorm room at night",
                "lighting": "soft blue LED glow as primary light source",
                "mood": "relaxing nighttime atmosphere"
            },
            "threshold": 0.85  # Standard threshold
        }
        
        # Create and execute flow
        print(f"\n🚀 Testing flow execution for: {product_info['name']}")
        flow = ImageGenerationFlow()
        
        # Use synchronous wrapper
        async def run_flow():
            return await flow.generate_image_for_product(
                product_id=product_id,
                reference_url=f"file://{reference_image_path.absolute()}",
                product_info=product_info
            )
        
        result = asyncio.run(run_flow())
        
        # Validate flow results
        assert result["success"], f"Flow failed: {result.get('error', 'Unknown error')}"
        assert result["attempts"] >= 1, "No generation attempts made"
        assert result["attempts"] <= 3, f"Too many attempts: {result['attempts']}"
        
        # Check metadata
        metadata = result.get("metadata", {})
        assert metadata.get("product_id") == str(product_id)
        assert metadata.get("completed_at") is not None
        
        print(f"✅ Flow completed in {result['attempts']} attempt(s)")
        
        # If image URL is available (Supabase configured), verify it
        if result.get("image_url"):
            assert result["image_url"].startswith("http"), "Invalid image URL format"
            print(f"✅ Image stored at: {result['image_url']}")
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for integration testing"
    )
    def test_flow_with_feedback_loop(self):
        """Test ImageGenerationFlow with rejection and feedback loop."""
        # Setup with higher threshold to potentially trigger feedback
        reference_image_path = Path(__file__).parent.parent / "reference_images" / "led-squirtle.jpg"
        assert reference_image_path.exists()
        
        product_id = uuid4()
        product_info = {
            "name": "Premium LED Squirtle Collector's Edition",
            "features": [
                "Ultra-bright blue LED with dimmer control",
                "Museum-quality Squirtle replica",
                "Premium materials and craftsmanship"
            ],
            "style": {
                "setting": "luxury dorm room showcase",
                "lighting": "dramatic blue LED accent lighting",
                "quality": "premium product photography"
            },
            "threshold": 0.95  # Very high threshold to test feedback loop
        }
        
        # Execute flow
        print(f"\n🚀 Testing feedback loop for: {product_info['name']}")
        flow = ImageGenerationFlow()
        
        async def run_flow():
            return await flow.generate_image_for_product(
                product_id=product_id,
                reference_url=f"file://{reference_image_path.absolute()}",
                product_info=product_info
            )
        
        result = asyncio.run(run_flow())
        
        # Validate results
        assert "attempts" in result, "No attempts information in result"
        assert result["attempts"] >= 1, "No generation attempts made"
        
        # Check if feedback was generated (if multiple attempts)
        if result["attempts"] > 1:
            metadata = result.get("metadata", {})
            feedback_history = metadata.get("feedback_history", [])
            assert len(feedback_history) > 0, "No feedback recorded despite multiple attempts"
            print(f"✅ Feedback loop activated: {len(feedback_history)} feedback rounds")
            
            # Verify feedback structure
            for feedback in feedback_history:
                assert "attempt" in feedback
                assert "feedback" in feedback
                assert "overall_score" in feedback
        
        print(f"✅ Flow completed after {result['attempts']} attempt(s)")
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for integration testing"
    )
    def test_error_handling(self):
        """Test error handling in the workflow."""
        # Test with invalid reference image
        crew = ImageGenerationCrew(
            product_id=uuid4(),
            reference_image_url="file:///nonexistent/image.jpg",
            product_name="Test Product",
            product_features=["Test feature"],
            style_requirements={"setting": "test"}
        )
        
        print("\n🚀 Testing error handling with invalid reference image")
        result = asyncio.run(crew.execute_async())
        
        # Should fail gracefully
        assert not result["success"], "Expected failure with invalid image"
        assert "error" in result, "No error message provided"
        print(f"✅ Error handled correctly: {result['error']}")
    
    @pytest.mark.integration
    def test_flow_state_tracking(self):
        """Test that flow properly tracks state throughout execution."""
        flow = ImageGenerationFlow()
        
        # Check initial state
        status = flow.get_generation_status()
        assert status["status"] == "not_started"
        assert status["attempts"] == 0
        assert not status["approved"]
        
        print("✅ Flow state tracking working correctly")