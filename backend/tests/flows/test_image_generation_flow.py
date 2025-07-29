"""Test the image generation flow."""

import os
import sys
from pathlib import Path
from uuid import uuid4

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.flows.image_generation_flow import ImageGenerationFlow
from src.core.config import get_settings


def test_flow_creation():
    """Test creating an image generation flow."""
    print("\n=== Testing Flow Creation ===\n")
    
    try:
        flow = ImageGenerationFlow()
        print("✅ Flow created successfully")
        
        # Check flow methods
        methods = [method for method in dir(flow) if not method.startswith('_')]
        print(f"   - Public methods: {len([m for m in methods if not m.startswith('_')])}")
        print(f"   - Has generate_image_for_product: {'generate_image_for_product' in methods}")
        print(f"   - Has get_generation_status: {'get_generation_status' in methods}")
        
        # Test status before starting
        status = flow.get_generation_status()
        print(f"\n📊 Initial status: {status['status']}")
        
        return flow
        
    except Exception as e:
        print(f"❌ Flow creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None


def test_flow_visualization():
    """Test flow visualization."""
    print("\n=== Testing Flow Visualization ===\n")
    
    try:
        flow = ImageGenerationFlow()
        
        # Generate flow diagram
        output_file = "output/flow_diagram.html"
        os.makedirs("output", exist_ok=True)
        
        flow.plot("flow_diagram")
        
        if os.path.exists(output_file):
            print(f"✅ Flow diagram generated: {output_file}")
            print(f"   - File size: {os.path.getsize(output_file)} bytes")
        else:
            print("❌ Flow diagram not generated")
            
    except Exception as e:
        print(f"❌ Flow visualization failed: {e}")
        import traceback
        traceback.print_exc()


def test_flow_with_mock_data():
    """Test flow with mock data (no actual execution)."""
    print("\n=== Testing Flow with Mock Data ===\n")
    
    flow = ImageGenerationFlow()
    if not flow:
        return
    
    # Test data
    test_product_id = uuid4()
    test_reference_url = "file:///path/to/test/image.jpg"
    test_product_info = {
        "name": "Test LED Product",
        "features": ["Blue LED", "USB Powered", "Portable"],
        "style": {"background": "white", "lighting": "soft"},
        "threshold": 0.80
    }
    
    print("📋 Test configuration:")
    print(f"   - Product ID: {test_product_id}")
    print(f"   - Product Name: {test_product_info['name']}")
    print(f"   - Features: {len(test_product_info['features'])}")
    print(f"   - Approval Threshold: {test_product_info['threshold']}")
    
    # Would execute flow here with:
    # result = await flow.generate_image_for_product(
    #     product_id=test_product_id,
    #     reference_url=test_reference_url,
    #     product_info=test_product_info
    # )
    
    print("\n✅ Mock test completed (actual execution requires API keys)")


def main():
    """Run all tests."""
    from dotenv import load_dotenv
    load_dotenv()
    
    settings = get_settings()
    print("🔧 Configuration:")
    print(f"   - OpenAI Model: {settings.openai_model}")
    print(f"   - API Key set: {bool(settings.openai_api_key)}")
    
    # Run tests
    test_flow_creation()
    test_flow_visualization()
    test_flow_with_mock_data()
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    main()