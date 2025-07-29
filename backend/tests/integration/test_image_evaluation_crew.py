"""Integration tests for ImageEvaluationCrew with real image evaluation."""

import os
import pytest
from pathlib import Path
from datetime import datetime
import shutil
from dotenv import load_dotenv

# Load environment
load_dotenv()

from src.crews.image_evaluation_crew import ImageEvaluationCrew


class TestImageEvaluationCrew:
    """Test the ImageEvaluationCrew with real images and evaluation."""
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for integration testing"
    )
    @pytest.mark.timeout(120)  # 2 minute timeout
    def test_evaluate_high_quality_image(self):
        """Test evaluating a high-quality image (should approve)."""
        # Setup - use the same image as reference and generated for high score
        reference_image_path = Path(__file__).parent.parent / "reference_images" / "led-squirtle.jpg"
        assert reference_image_path.exists(), f"Reference image not found at {reference_image_path}"
        
        reference_url = f"file://{reference_image_path.absolute()}"
        generated_path = reference_url  # Same image should get high score
        
        # Create evaluation crew
        crew = ImageEvaluationCrew(
            reference_url=reference_url,
            generated_path=generated_path,
            product_name="LED Squirtle Night Light",
            threshold=0.85
        )
        
        print(f"\n🔍 Evaluating high-quality image...")
        print(f"📸 Reference: {reference_url}")
        print(f"📸 Generated: {generated_path}")
        print(f"📊 Threshold: 85%")
        
        # Execute evaluation
        result = crew.evaluate()
        
        # Validate results
        assert result["success"], f"Evaluation failed: {result.get('error', 'Unknown error')}"
        assert result["approved"], "High-quality image should be approved"
        assert result["overall_score"] >= 85, f"Score too low: {result['overall_score']}"
        
        # Check individual scores
        scores = result.get("scores", {})
        print(f"\n✅ Evaluation Results:")
        print(f"   - Overall Score: {result['overall_score']}/100")
        print(f"   - Approved: {result['approved']}")
        print(f"   - Individual Scores: {scores}")
        
        # Verify score categories exist
        expected_categories = ["visual_fidelity", "product_accuracy", "technical_quality"]
        for category in expected_categories:
            if category in scores:
                assert scores[category] > 70, f"{category} score too low: {scores[category]}"
        
        # Should have minimal or no feedback for identical images
        feedback = result.get("feedback", [])
        print(f"   - Feedback items: {len(feedback)}")
        if feedback:
            print(f"   - Feedback: {feedback}")
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for integration testing"
    )
    @pytest.mark.timeout(120)
    def test_evaluate_different_image(self):
        """Test evaluating a different image (should reject with feedback)."""
        # Setup - use different images
        reference_image_path = Path(__file__).parent.parent / "reference_images" / "led-squirtle.jpg"
        assert reference_image_path.exists()
        
        # For testing, we'll use a generated image if available
        generated_images_dir = Path("output/generated_images")
        generated_image = None
        
        if generated_images_dir.exists():
            # Find a generated image
            for img in generated_images_dir.glob("*.png"):
                generated_image = img
                break
        
        if not generated_image:
            # If no generated image, create a simple different image for testing
            print("⚠️  No generated images found, skipping different image test")
            pytest.skip("No generated images available for comparison")
        
        reference_url = f"file://{reference_image_path.absolute()}"
        generated_path = f"file://{generated_image.absolute()}"
        
        # Create evaluation crew with high threshold
        crew = ImageEvaluationCrew(
            reference_url=reference_url,
            generated_path=generated_path,
            product_name="LED Squirtle Night Light",
            threshold=0.95  # Very high threshold
        )
        
        print(f"\n🔍 Evaluating different images...")
        print(f"📸 Reference: {reference_url}")
        print(f"📸 Generated: {generated_path}")
        print(f"📊 Threshold: 95% (very high)")
        
        # Execute evaluation
        result = crew.evaluate()
        
        # Validate results
        assert result["success"], f"Evaluation failed: {result.get('error', 'Unknown error')}"
        
        print(f"\n📊 Evaluation Results:")
        print(f"   - Overall Score: {result['overall_score']}/100")
        print(f"   - Approved: {result['approved']}")
        print(f"   - Scores: {result.get('scores', {})}")
        
        # With 95% threshold, even good images might be rejected
        if not result["approved"]:
            # Should have specific feedback
            feedback = result.get("feedback", [])
            assert len(feedback) > 0, "Rejected image should have feedback"
            
            print(f"   - Feedback ({len(feedback)} items):")
            for fb in feedback:
                print(f"     • {fb}")
            
            # Verify feedback is actionable
            for fb in feedback:
                assert len(fb) > 10, "Feedback should be detailed"
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for integration testing"
    )
    def test_evaluation_score_parsing(self):
        """Test that evaluation scores are properly parsed."""
        reference_image_path = Path(__file__).parent.parent / "reference_images" / "led-squirtle.jpg"
        assert reference_image_path.exists()
        
        reference_url = f"file://{reference_image_path.absolute()}"
        
        crew = ImageEvaluationCrew(
            reference_url=reference_url,
            generated_path=reference_url,
            product_name="Test Product",
            threshold=0.80
        )
        
        print(f"\n🔍 Testing score parsing...")
        
        # Execute evaluation
        result = crew.evaluate()
        
        assert result["success"], "Evaluation should succeed"
        
        # Check score structure
        assert "overall_score" in result, "Should have overall_score"
        assert isinstance(result["overall_score"], (int, float)), "Score should be numeric"
        assert 0 <= result["overall_score"] <= 100, "Score should be 0-100"
        
        # Check individual scores if present
        if "scores" in result:
            scores = result["scores"]
            print(f"\n📊 Parsed scores: {scores}")
            
            for category, score in scores.items():
                assert isinstance(score, (int, float)), f"{category} score should be numeric"
                assert 0 <= score <= 100, f"{category} score should be 0-100"
        
        # Check approval decision
        assert "approved" in result, "Should have approval decision"
        assert isinstance(result["approved"], bool), "Approval should be boolean"
        
        # Check feedback structure
        if "feedback" in result:
            feedback = result["feedback"]
            assert isinstance(feedback, list), "Feedback should be a list"
            for item in feedback:
                assert isinstance(item, str), "Feedback items should be strings"
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for integration testing"
    )
    def test_evaluation_with_invalid_images(self):
        """Test evaluation handles invalid image paths gracefully."""
        crew = ImageEvaluationCrew(
            reference_url="file:///nonexistent/reference.jpg",
            generated_path="file:///nonexistent/generated.jpg",
            product_name="Invalid Test",
            threshold=0.85
        )
        
        print(f"\n🔍 Testing error handling with invalid images...")
        
        # Should handle the error gracefully
        result = crew.evaluate()
        
        # The crew might still return success=True but with low scores
        # or it might return success=False with an error
        if not result["success"]:
            assert "error" in result, "Failed evaluation should have error message"
            print(f"✅ Error handled correctly: {result['error']}")
        else:
            # If it somehow succeeds, scores should be very low
            assert result["overall_score"] < 50, "Invalid images should get low scores"
            assert not result["approved"], "Invalid images should not be approved"
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for integration testing"
    )
    @pytest.mark.timeout(180)  # 3 minute timeout
    def test_evaluation_consistency(self):
        """Test that evaluation is relatively consistent across runs."""
        reference_image_path = Path(__file__).parent.parent / "reference_images" / "led-squirtle.jpg"
        assert reference_image_path.exists()
        
        reference_url = f"file://{reference_image_path.absolute()}"
        
        print(f"\n🔍 Testing evaluation consistency (2 runs)...")
        
        scores = []
        approvals = []
        
        # Run evaluation twice
        for i in range(2):
            crew = ImageEvaluationCrew(
                reference_url=reference_url,
                generated_path=reference_url,
                product_name="Consistency Test",
                threshold=0.85
            )
            
            result = crew.evaluate()
            assert result["success"], f"Run {i+1} failed"
            
            scores.append(result["overall_score"])
            approvals.append(result["approved"])
            
            print(f"   Run {i+1}: Score={result['overall_score']}, Approved={result['approved']}")
        
        # Check consistency
        score_diff = abs(scores[0] - scores[1])
        assert score_diff <= 10, f"Scores vary too much: {scores[0]} vs {scores[1]}"
        
        # Approval decisions should be the same for identical images
        assert approvals[0] == approvals[1], "Approval decisions should be consistent"
        
        print(f"✅ Evaluation is consistent (score difference: {score_diff})")