#!/usr/bin/env python
"""Test script for image generation workflow."""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from src.workflows.image_generation_workflow import ImageGenerationWorkflow


async def test_image_generation():
    """Test the image generation workflow with mock data."""
    
    print("=== Image Generation Workflow Test ===\n")
    
    # Create workflow instance
    workflow = ImageGenerationWorkflow(max_attempts=2)
    
    # Test data
    test_data = {
        "product_id": "test-product-123",
        "reference_image_url": "https://example.com/reference-image.jpg",
        "product_name": "Premium Wireless Headphones",
        "product_features": [
            "Active noise cancellation",
            "40-hour battery life",
            "Premium leather cushions",
            "Foldable design"
        ],
        "style_requirements": {
            "background": "pure white",
            "lighting": "studio lighting with soft shadows",
            "angle": "45-degree product shot"
        },
        "approval_threshold": 0.85
    }
    
    print(f"Product: {test_data['product_name']}")
    print(f"Features: {', '.join(test_data['product_features'])}")
    print(f"Reference: {test_data['reference_image_url']}")
    print(f"Approval threshold: {test_data['approval_threshold'] * 100}%")
    print("\nStarting image generation workflow...")
    
    try:
        # This would normally call the actual workflow
        # For testing, we'll just show what would happen
        print("\n[MOCK] Step 1: Downloading reference image...")
        print("[MOCK] Step 2: Generating initial image with gpt-image-1...")
        print("[MOCK] Step 3: Evaluating generated image with GPT-4 vision...")
        print("[MOCK] Step 4: Score: 78% - Below threshold")
        print("[MOCK] Step 5: Feedback: ['Improve product lighting', 'Show logo more clearly']")
        print("[MOCK] Step 6: Regenerating with enhanced prompt...")
        print("[MOCK] Step 7: Re-evaluating new image...")
        print("[MOCK] Step 8: Score: 92% - Approved!")
        print("[MOCK] Step 9: Uploading to Supabase storage...")
        print("[MOCK] Step 10: Complete!")
        
        # Mock result
        result = {
            "success": True,
            "image_url": "https://storage.example.com/products/test-product-123/final.png",
            "score": 0.92,
            "attempts": 2,
            "prompt": "Professional product photography of Premium Wireless Headphones..."
        }
        
        print(f"\n✓ Image generated successfully!")
        print(f"  URL: {result['image_url']}")
        print(f"  Score: {result['score'] * 100}%")
        print(f"  Attempts: {result['attempts']}")
        
    except Exception as e:
        print(f"\n✗ Error: {str(e)}")
        return False
    
    return True


async def test_api_request():
    """Show example API request."""
    print("\n\n=== Example API Request ===\n")
    
    print("POST /api/v1/images/generate")
    print("Content-Type: application/json")
    print("\nRequest body:")
    print("""{
    "product_id": "prod-12345",
    "reference_image_url": "https://example.com/reference.jpg",
    "product_name": "Smart Watch Pro",
    "product_features": ["Heart rate monitor", "GPS tracking", "Water resistant"],
    "style_requirements": {
        "background": "gradient",
        "lighting": "dramatic"
    },
    "approval_threshold": 0.85,
    "max_attempts": 3
}""")
    
    print("\nExpected response:")
    print("""{
    "success": true,
    "image_url": "https://storage.supabase.co/products/prod-12345/generated_2.png",
    "score": 0.88,
    "attempts": 2,
    "prompt": "Professional product photography of Smart Watch Pro..."
}""")


if __name__ == "__main__":
    print("Image Generation System Test\n")
    
    # Run workflow test
    asyncio.run(test_image_generation())
    
    # Show API example
    asyncio.run(test_api_request())
    
    print("\n\nNote: This is a mock test. To run actual image generation:")
    print("1. Ensure OPENAI_API_KEY is set in .env")
    print("2. Ensure SUPABASE_URL and SUPABASE_SERVICE_KEY are set")
    print("3. Start the API server: poetry run python run.py")
    print("4. Send requests to POST /api/v1/images/generate")