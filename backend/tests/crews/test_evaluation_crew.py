"""Test the image evaluation crew."""

import os
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.crews.image_evaluation_crew import ImageEvaluationCrew
from src.core.config import get_settings


def test_evaluation_crew_creation():
    """Test creating an evaluation crew."""
    print("\n=== Testing Evaluation Crew Creation ===\n")
    
    # Test configuration
    reference_image_path = "tests/reference_images/led-squirtle.jpg"
    
    if not os.path.exists(reference_image_path):
        print(f"❌ Reference image not found: {reference_image_path}")
        return
    
    reference_url = f"file://{os.path.abspath(reference_image_path)}"
    generated_path = reference_url  # For testing, use same image
    
    # Create crew
    print("🚀 Creating evaluation crew...")
    crew = ImageEvaluationCrew(
        reference_url=reference_url,
        generated_path=generated_path,
        product_name="LED Squirtle Test",
        threshold=0.85
    )
    
    print("✅ Crew created successfully")
    
    # Test components
    print("\n📋 Testing components:")
    
    try:
        evaluator = crew.image_evaluator()
        print(f"✅ Evaluator agent created: {evaluator.role}")
        print(f"   - Multimodal: {evaluator.multimodal}")
        print(f"   - Tools: {len(evaluator.tools)} (should be 0)")
        
        eval_task = crew.evaluate_image_task()
        print(f"✅ Evaluation task created")
        
        crew_instance = crew.crew()
        print(f"✅ Crew instance created")
        print(f"   - Agents: {len(crew_instance.agents)}")
        print(f"   - Tasks: {len(crew_instance.tasks)}")
        
    except Exception as e:
        print(f"❌ Component creation failed: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n✅ All components created successfully!")
    return crew


def main():
    """Run the test."""
    from dotenv import load_dotenv
    load_dotenv()
    
    settings = get_settings()
    print("🔧 Configuration:")
    print(f"   - OpenAI Model: {settings.openai_model}")
    print(f"   - API Key set: {bool(settings.openai_api_key)}")
    
    if not settings.openai_api_key:
        print("\n⚠️  ERROR: OpenAI API key not set!")
        print("Please set OPENAI_API_KEY in your .env file")
        return
    
    crew = test_evaluation_crew_creation()
    
    if crew:
        print("\n📊 Would you like to run a test evaluation? (y/n): ", end="")
        # For automated testing, we'll skip the actual evaluation
        print("n (skipping for automated test)")


if __name__ == "__main__":
    main()