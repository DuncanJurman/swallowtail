"""Test script for Image Generation with CrewAI configuration."""

import asyncio
import os
import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.workflows.image_generation_workflow import ImageGenerationWorkflow
from src.services.storage import SupabaseStorageService
from src.core.config import get_settings


async def test_image_generation_with_crew():
    """Test the new CrewAI-based image generation workflow."""
    print("\n=== Testing Image Generation with CrewAI Configuration ===\n")
    
    # Test configuration
    test_product_id = str(uuid4())
    reference_image_path = "tests/reference_images/led-squirtle.jpg"
    
    # Check if reference image exists
    if not os.path.exists(reference_image_path):
        print(f"❌ Reference image not found at: {reference_image_path}")
        return
    
    print(f"✅ Found reference image: {reference_image_path}")
    
    # For testing purposes, we'll use a local file URL instead of uploading to storage
    # This avoids the need for a product in the database
    reference_url = f"file://{os.path.abspath(reference_image_path)}"
    print(f"📁 Using local reference image: {reference_url}")
    
    # Test parameters
    test_params = {
        "product_id": test_product_id,
        "reference_image_url": reference_url,
        "product_name": "LED Squirtle Night Light",
        "product_features": [
            "Glowing blue LED light",
            "Squirtle Pokemon character",
            "Perfect for dorm room decoration"
        ],
        "style_requirements": {
            "background": "modern dorm room setting",
            "lighting": "blue LED light illuminating the room",
            "atmosphere": "cozy night-time ambiance"
        },
        "approval_threshold": 0.80  # 80% threshold for testing
    }
    
    # Create workflow instance
    workflow = ImageGenerationWorkflow(max_attempts=3)
    
    print("\n🚀 Starting image generation workflow with CrewAI...\n")
    print(f"Product: {test_params['product_name']}")
    print(f"Features: {', '.join(test_params['product_features'])}")
    print(f"Style: {test_params['style_requirements']}")
    print(f"Approval threshold: {test_params['approval_threshold'] * 100}%")
    print(f"Max attempts: {workflow.max_attempts}")
    
    # Test 1: Use the new CrewAI-based method
    print("\n--- Test 1: CrewAI-based Generation ---")
    start_time = datetime.now()
    
    try:
        result = await workflow.generate_product_image_with_crew(**test_params)
        
        elapsed_time = (datetime.now() - start_time).total_seconds()
        print(f"\n⏱️  Workflow completed in {elapsed_time:.1f} seconds")
        
        if result.get('success'):
            print(f"✅ Image generation successful!")
            print(f"   - Image URL: {result['image_url']}")
            print(f"   - Overall Score: {result['score'] * 100:.1f}%")
            print(f"   - Attempts: {result['attempts']}")
            print(f"   - Prompt: {result['prompt'][:100]}...")
            
            if result.get('detailed_scores'):
                print("\n📊 Detailed Scores:")
                scores = result['detailed_scores']
                print(f"   - Visual Fidelity: {scores.get('visual_fidelity', 'N/A')}%")
                print(f"   - Prompt Accuracy: {scores.get('prompt_accuracy', 'N/A')}%")
                print(f"   - Technical Quality: {scores.get('technical_quality', 'N/A')}%")
                print(f"   - Product Accuracy: {scores.get('product_accuracy', 'N/A')}%")
        else:
            print(f"❌ Image generation failed!")
            print(f"   - Error: {result.get('error', 'Unknown error')}")
            print(f"   - Attempts: {result.get('attempts', 0)}")
            
            if result.get('image_url'):
                print(f"   - Best attempt saved at: {result['image_url']}")
                print(f"   - Best score: {result.get('score', 0) * 100:.1f}%")
    
    except Exception as e:
        print(f"❌ Workflow error: {str(e)}")
        import traceback
        traceback.print_exc()
    
    # Test 2: Compare with direct agent method (optional)
    print("\n--- Test 2: Direct Agent Method (for comparison) ---")
    start_time = datetime.now()
    
    try:
        result = await workflow.generate_product_image(**test_params)
        
        elapsed_time = (datetime.now() - start_time).total_seconds()
        print(f"\n⏱️  Direct method completed in {elapsed_time:.1f} seconds")
        
        if result.get('success'):
            print(f"✅ Direct generation successful!")
            print(f"   - Score: {result['score'] * 100:.1f}%")
            print(f"   - Attempts: {result['attempts']}")
        else:
            print(f"❌ Direct generation failed: {result.get('error')}")
    
    except Exception as e:
        print(f"❌ Direct method error: {str(e)}")
    
    print("\n=== Test Complete ===\n")


async def test_yaml_config_loading():
    """Test that agents are properly loading from YAML configuration."""
    print("\n=== Testing YAML Configuration Loading ===\n")
    
    try:
        # Test Image Generation Agent
        from src.agents.image_generation import ImageGenerationAgent
        gen_agent = ImageGenerationAgent()
        
        print("✅ Image Generation Agent loaded")
        print(f"   - Name: {gen_agent.name}")
        print(f"   - Role: {gen_agent.role}")
        # These attributes are on the internal CrewAI agent, not our BaseAgent
        if hasattr(gen_agent, 'agent') and gen_agent.agent:
            print(f"   - Agent LLM: {type(gen_agent.agent.llm).__name__}")
        
        # Test Image Evaluator Agent
        from src.agents.image_evaluator import ImageEvaluatorAgent
        eval_agent = ImageEvaluatorAgent()
        
        print("\n✅ Image Evaluator Agent loaded")
        print(f"   - Name: {eval_agent.name}")
        print(f"   - Role: {eval_agent.role}")
        if hasattr(eval_agent, 'agent') and eval_agent.agent:
            print(f"   - Agent LLM: {type(eval_agent.agent.llm).__name__}")
        
        # Test loading from YAML directly
        from src.crews.base import SwallowtailCrewBase
        crew_base = SwallowtailCrewBase()
        
        # Create agents from YAML config
        gen_from_yaml = crew_base.create_agent("image_generator")
        eval_from_yaml = crew_base.create_agent("image_evaluator")
        
        print("\n✅ Agents created from YAML config")
        print(f"   - Generator role: {gen_from_yaml.role}")
        print(f"   - Evaluator role: {eval_from_yaml.role}")
        
    except Exception as e:
        print(f"❌ Configuration loading failed: {str(e)}")
        import traceback
        traceback.print_exc()


async def main():
    """Run all tests."""
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()
    
    # Verify required settings
    settings = get_settings()
    if not settings.openai_api_key:
        print("❌ OPENAI_API_KEY not set in environment")
        return
    
    if not settings.supabase_url or not settings.supabase_service_key:
        print("❌ Supabase credentials not set in environment")
        return
    
    print("✅ Environment variables loaded")
    
    # Run tests
    await test_yaml_config_loading()
    await test_image_generation_with_crew()


if __name__ == "__main__":
    asyncio.run(main())