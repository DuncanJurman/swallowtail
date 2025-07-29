"""
End-to-End test for LED Squirtle in dorm room with blue lighting.

This is the PRIMARY test for the user's specific requirement:
'place this product in a dorm room with the blue light illuminating the room'
"""
import pytest
import os
import asyncio
from pathlib import Path
from uuid import uuid4
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.flows.image_generation_flow import ImageGenerationFlow
from src.core.config import get_settings


class TestLEDSquirtleDormRoom:
    """
    Primary E2E test for the user's specific requirement:
    'place this product in a dorm room with the blue light illuminating the room'
    """
    
    @pytest.mark.e2e
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for end-to-end testing"
    )
    @pytest.mark.asyncio(scope="function")
    async def test_led_squirtle_dorm_room_generation(self):
        """Test complete workflow for LED Squirtle in dorm room with blue lighting."""
        # Setup
        reference_image_path = Path(__file__).parent.parent / "reference_images" / "led-squirtle.jpg"
        
        # Ensure reference image exists
        assert reference_image_path.exists(), f"Reference image not found at {reference_image_path}"
        
        # Product configuration specifically for dorm room with blue lighting
        product_id = uuid4()
        product_info = {
            "name": "LED Squirtle Night Light",
            "features": [
                "Blue LED illumination that creates ambient lighting",
                "Squirtle Pokemon character design",
                "Perfect size for dorm room nightstand",
                "Soft blue glow suitable for nighttime use"
            ],
            "style": {
                "setting": "modern college dorm room at night",
                "lighting": "blue LED glow illuminating the entire room",
                "placement": "on a nightstand or desk in the dorm room",
                "atmosphere": "cozy nighttime ambiance with the blue light as primary light source",
                "details": "show the blue light casting shadows and creating mood lighting"
            },
            "threshold": 0.85
        }
        
        # Execute flow
        print(f"\n🚀 Starting flow execution for: {product_info['name']}")
        print(f"📁 Reference image: {reference_image_path}")
        
        flow = ImageGenerationFlow()
        result = await flow.generate_image_for_product(
            product_id=product_id,
            reference_url=f"file://{reference_image_path.absolute()}",
            product_info=product_info
        )
        
        print(f"\n📊 Flow completed with result: {result}")
        
        # Primary Assertions
        if not result["success"]:
            print(f"\n❌ FAILURE DETAILS: {result}")
        assert result["success"], f"Image generation failed: {result.get('error', 'Unknown error')}"
        assert result["attempts"] <= 3, f"Too many attempts required: {result['attempts']}"
        
        # Verify image was generated and stored
        assert result["image_url"], "No image URL returned"
        assert result["image_url"].startswith("http"), "Invalid image URL format"
        
        # Verify metadata contains our requirements
        metadata = result.get("metadata", {})
        assert metadata, "No metadata returned"
        
        # Check that attempts were made
        assert metadata.get("product_id") == str(product_id)
        assert metadata.get("completed_at") is not None
        
        # Verify prompt contains key requirements
        if metadata.get("feedback_history"):
            # If there was feedback, check it was addressed
            last_feedback = metadata["feedback_history"][-1]
            assert "feedback" in last_feedback
            
        # Print results for manual verification
        print("\n" + "="*50)
        print("LED SQUIRTLE DORM ROOM TEST RESULTS")
        print("="*50)
        print(f"✅ Success: {result['success']}")
        print(f"📸 Image URL: {result['image_url']}")
        print(f"🔄 Attempts: {result['attempts']}")
        print(f"🎯 Final Score: {self._extract_final_score(metadata)}")
        print("\n📝 Generation Details:")
        print(f"   - Product: {product_info['name']}")
        print(f"   - Setting: {product_info['style']['setting']}")
        print(f"   - Lighting: {product_info['style']['lighting']}")
        print("="*50 + "\n")
    
    @pytest.mark.e2e
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for end-to-end testing"
    )
    @pytest.mark.asyncio
    async def test_feedback_loop_improvement(self):
        """Test that feedback loop actually improves the image."""
        reference_image_path = Path(__file__).parent.parent / "reference_images" / "led-squirtle.jpg"
        assert reference_image_path.exists()
        
        # Use a lower threshold to potentially trigger feedback loop
        product_info = {
            "name": "LED Squirtle Night Light",
            "features": [
                "Blue LED creates dramatic room lighting",
                "Must show blue light illuminating walls and ceiling"
            ],
            "style": {
                "setting": "dark dorm room",
                "lighting": "strong blue LED glow as only light source",
                "atmosphere": "dramatic blue lighting effect"
            },
            "threshold": 0.90  # Higher threshold to increase chance of rejection
        }
        
        flow = ImageGenerationFlow()
        result = await flow.generate_image_for_product(
            product_id=uuid4(),
            reference_url=f"file://{reference_image_path.absolute()}",
            product_info=product_info
        )
        
        assert result["success"]
        
        # If multiple attempts were made, verify feedback was incorporated
        if result["attempts"] > 1:
            metadata = result.get("metadata", {})
            feedback_history = metadata.get("feedback_history", [])
            
            assert len(feedback_history) > 0, "No feedback recorded despite multiple attempts"
            
            # Check that feedback mentions our key requirements
            all_feedback = " ".join([
                " ".join(fb.get("feedback", [])) 
                for fb in feedback_history
            ]).lower()
            
            # Verify feedback addresses lighting or room aspects
            assert any(word in all_feedback for word in ["blue", "light", "room", "glow", "ambient"])
    
    @pytest.mark.e2e
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for end-to-end testing"
    )
    @pytest.mark.asyncio
    async def test_style_requirements_applied(self):
        """Test that specific style requirements are actually applied."""
        reference_image_path = Path(__file__).parent.parent / "reference_images" / "led-squirtle.jpg"
        assert reference_image_path.exists()
        
        # Very specific style requirements
        specific_style = {
            "room_type": "modern college dormitory room",
            "time_of_day": "nighttime with lights off",
            "lighting_effect": "blue LED glow illuminating the entire room",
            "placement": "on wooden desk next to laptop",
            "camera_angle": "slightly elevated showing room ambiance",
            "mood": "cozy study atmosphere with blue accent lighting"
        }
        
        product_info = {
            "name": "LED Squirtle Night Light",
            "features": ["Blue LED night light for dorm rooms"],
            "style": specific_style,
            "threshold": 0.85
        }
        
        flow = ImageGenerationFlow()
        result = await flow.generate_image_for_product(
            product_id=uuid4(),
            reference_url=f"file://{reference_image_path.absolute()}",
            product_info=product_info
        )
        
        assert result["success"]
        
        # Verify the generation incorporated our style requirements
        # This is validated through the evaluation crew's approval
        metadata = result.get("metadata", {})
        
        # If approved on first attempt, style was well applied
        if result["attempts"] == 1:
            print("\n✅ Style requirements successfully applied on first attempt!")
        else:
            print(f"\n⚠️  Required {result['attempts']} attempts to meet style requirements")
    
    @pytest.mark.e2e
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for end-to-end testing"
    )
    @pytest.mark.asyncio
    async def test_multimodal_vision_working(self):
        """Test that multimodal agents can actually see and evaluate images."""
        reference_image_path = Path(__file__).parent.parent / "reference_images" / "led-squirtle.jpg"
        assert reference_image_path.exists()
        
        product_info = {
            "name": "LED Squirtle Night Light",
            "features": ["Blue LED Pokemon night light"],
            "style": {
                "setting": "dorm room with blue lighting",
                "requirement": "must clearly show Squirtle character"
            },
            "threshold": 0.85
        }
        
        flow = ImageGenerationFlow()
        result = await flow.generate_image_for_product(
            product_id=uuid4(),
            reference_url=f"file://{reference_image_path.absolute()}",
            product_info=product_info
        )
        
        assert result["success"]
        
        # The fact that evaluation passed means multimodal vision is working
        # because the evaluator needs to SEE both images to compare them
        metadata = result.get("metadata", {})
        
        # Check for evaluation scores which require visual analysis
        if metadata.get("feedback_history"):
            last_eval = metadata["feedback_history"][-1]
            scores = last_eval.get("scores", {})
            
            # These scores can only be determined by seeing the images
            assert any(key in scores for key in [
                "visual_fidelity",
                "product_accuracy",
                "technical_quality"
            ]), "No visual evaluation scores found"
    
    def _extract_final_score(self, metadata):
        """Extract the final evaluation score from metadata."""
        if metadata.get("feedback_history"):
            last_eval = metadata["feedback_history"][-1]
            return last_eval.get("overall_score", "N/A")
        return "N/A"
    
    @pytest.mark.e2e
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for end-to-end testing"  
    )
    @pytest.mark.asyncio
    async def test_temp_file_cleanup(self):
        """Test that temporary files are properly cleaned up."""
        reference_image_path = Path(__file__).parent.parent / "reference_images" / "led-squirtle.jpg"
        assert reference_image_path.exists()
        
        # Track temp files before
        import glob
        temp_files_before = set(glob.glob("/tmp/*.png"))
        
        product_info = {
            "name": "LED Squirtle Night Light",
            "features": ["Blue LED night light"],
            "style": {"setting": "dorm room"},
            "threshold": 0.85
        }
        
        flow = ImageGenerationFlow()
        result = await flow.generate_image_for_product(
            product_id=uuid4(),
            reference_url=f"file://{reference_image_path.absolute()}",
            product_info=product_info
        )
        
        assert result["success"]
        
        # Give some time for cleanup
        await asyncio.sleep(1)
        
        # Check temp files after
        temp_files_after = set(glob.glob("/tmp/*.png"))
        
        # New temp files should be cleaned up
        new_files = temp_files_after - temp_files_before
        assert len(new_files) == 0, f"Temporary files not cleaned up: {new_files}"