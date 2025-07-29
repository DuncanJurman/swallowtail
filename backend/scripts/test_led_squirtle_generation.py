#!/usr/bin/env python
"""Test image generation with LED Squirtle reference image."""

import asyncio
import sys
from pathlib import Path
import os
from datetime import datetime
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

from src.workflows.image_generation_workflow import ImageGenerationWorkflow
from src.services.storage import SupabaseStorageService


async def test_led_squirtle_generation():
    """Test image generation with actual LED Squirtle reference."""
    
    print("=== LED Squirtle Image Generation Test ===\n")
    
    # First, we need to upload the reference image to a URL (or use local file handling)
    # For now, we'll create a modified workflow that accepts local files
    
    # Create a test workflow that uses a local reference image
    workflow = ImageGenerationWorkflow(max_attempts=3)
    
    # Since the workflow expects a URL, we'll need to modify our approach
    # Let's create a direct test using the agents
    from src.agents.image_generation import ImageGenerationAgent
    from src.agents.image_evaluator import ImageEvaluatorAgent
    from src.services.openai_image_service import OpenAIImageService
    
    # Read the reference image
    reference_path = Path(__file__).parent.parent / "tests/reference_images/led-squirtle.jpg"
    
    if not reference_path.exists():
        print(f"Error: Reference image not found at {reference_path}")
        return False
        
    print(f"✓ Found reference image: {reference_path}")
    
    # Read image data
    with open(reference_path, 'rb') as f:
        reference_data = f.read()
    
    print(f"✓ Loaded reference image ({len(reference_data) / 1024:.1f} KB)")
    
    # Create OpenAI service directly
    openai_service = OpenAIImageService()
    
    # Prepare the image
    print("\nPreparing image for API...")
    try:
        prepared_image = await openai_service.prepare_image(reference_data)
        print(f"✓ Image prepared ({len(prepared_image) / 1024:.1f} KB)")
    except Exception as e:
        print(f"✗ Error preparing image: {e}")
        return False
    
    # Create generation prompt
    prompt = """Professional product photography of LED Squirtle night light in a cozy bedroom setting.
    
IMPORTANT REQUIREMENTS:
- Place the LED Squirtle on a bedside table in a dimly lit bedroom
- The Squirtle's blue LED light should be ON and glowing
- The blue light should create a soft, ambient illumination throughout the room
- Show the light casting a gentle blue glow on nearby walls and ceiling
- Include bedroom elements: bed with pillows, perhaps a book or clock on the nightstand
- Overall mood: calm, peaceful nighttime atmosphere
- The blue LED glow should be the primary light source in the room
- Maintain the exact product design and features from the reference image"""
    
    print("\nGenerating image with OpenAI gpt-image-1...")
    print("Prompt:", prompt[:100] + "...")
    
    try:
        # Generate the image
        result = await openai_service.generate_image(
            reference_image=prepared_image,
            prompt=prompt,
            size="1024x1024",
            quality="hd"
        )
        
        print("✓ Image generated successfully!")
        
        # Save the generated image
        output_dir = Path(__file__).parent.parent / "output/generated_images"
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"led_squirtle_bedroom_{timestamp}.png"
        
        with open(output_path, 'wb') as f:
            f.write(result.image_data)
            
        print(f"\n✓ Generated image saved to: {output_path}")
        print(f"  Size: {len(result.image_data) / 1024:.1f} KB")
        
        # Now evaluate the generated image
        print("\nEvaluating generated image quality...")
        
        eval_result = await openai_service.evaluate_images(
            reference_image=reference_data,
            generated_image=result.image_data,
            original_prompt=prompt,
            approval_threshold=0.80
        )
        
        print(f"\n📊 Evaluation Results (Structured Output):")
        print(f"  Overall Score: {eval_result.score * 100:.1f}%")
        print(f"  Approved: {'✓ Yes' if eval_result.approved else '✗ No'}")
        
        # Show detailed scores from structured response
        if eval_result.metadata:
            print(f"\n  Detailed Scores:")
            print(f"    Visual Fidelity: {eval_result.metadata['visual_fidelity_score']}%")
            print(f"    Prompt Accuracy: {eval_result.metadata['prompt_accuracy_score']}%")
            print(f"    Technical Quality: {eval_result.metadata['technical_quality_score']}%")
            print(f"    Product Accuracy: {eval_result.metadata['product_accuracy_score']}%")
            
            if eval_result.metadata.get('issues'):
                print(f"\n  Issues Found:")
                for issue in eval_result.metadata['issues']:
                    print(f"    ⚠️  {issue}")
        
        if eval_result.feedback:
            print(f"\n  Suggested Improvements:")
            for item in eval_result.feedback:
                print(f"    💡 {item}")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Error generating image: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Run the test."""
    # Check for API key
    if not os.getenv("OPENAI_API_KEY"):
        print("Error: OPENAI_API_KEY not found in environment")
        print("Please set it in your .env file or export it")
        return
    
    success = await test_led_squirtle_generation()
    
    if success:
        print("\n✅ Test completed successfully!")
        print("\nCheck the output/generated_images directory for the result.")
    else:
        print("\n❌ Test failed!")


if __name__ == "__main__":
    asyncio.run(main())