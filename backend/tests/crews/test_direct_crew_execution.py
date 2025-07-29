"""Direct test of crew execution to debug issues."""
import asyncio
import os
import sys
from pathlib import Path
from uuid import uuid4
from dotenv import load_dotenv

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()

from src.crews.image_generation_crew import ImageGenerationCrew


async def test_direct_crew():
    """Test crew execution directly without flow."""
    print("\n=== Direct Crew Execution Test ===\n")
    
    # Reference image
    reference_image_path = Path(__file__).parent / "reference_images" / "led-squirtle.jpg"
    
    if not reference_image_path.exists():
        print(f"❌ Reference image not found at: {reference_image_path}")
        return
    
    print(f"✅ Found reference image: {reference_image_path}")
    
    # Create crew
    crew = ImageGenerationCrew(
        product_id=uuid4(),
        reference_image_url=f"file://{reference_image_path.absolute()}",
        product_name="LED Squirtle Night Light",
        product_features=[
            "Blue LED illumination",
            "Squirtle Pokemon character",
            "Perfect for dorm room"
        ],
        style_requirements={
            "setting": "modern dorm room at night",
            "lighting": "blue LED glow illuminating the room",
            "atmosphere": "cozy nighttime ambiance"
        }
    )
    
    print("\n🚀 Executing crew...")
    
    try:
        # Try direct execution
        result = await crew.execute_async()
        
        print(f"\n📊 Result: {result}")
        
        if result.get("success"):
            print("\n✅ Success!")
            print(f"   - Output length: {len(result.get('output', ''))}")
            print(f"   - Temp path: {result.get('temp_image_path')}")
            print(f"   - Storage URL: {result.get('storage_url')}")
        else:
            print(f"\n❌ Failed: {result.get('error')}")
            
    except Exception as e:
        print(f"\n❌ Exception: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_direct_crew())