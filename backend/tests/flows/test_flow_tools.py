"""Test the flow tools."""

import os
import sys
from pathlib import Path
from uuid import uuid4

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from src.tools.flow_tools import create_flow_tools
from src.core.config import get_settings


def test_flow_tool_creation():
    """Test creating flow tools."""
    print("\n=== Testing Flow Tool Creation ===\n")
    
    try:
        # Create tools
        generation_tool, status_tool = create_flow_tools()
        
        print("✅ Flow tools created successfully")
        print(f"   - Generation tool: {generation_tool.name}")
        print(f"   - Status tool: {status_tool.name}")
        
        # Check tool descriptions
        print(f"\n📋 Generation tool description length: {len(generation_tool.description)}")
        print(f"📋 Status tool description length: {len(status_tool.description)}")
        
        return generation_tool, status_tool
        
    except Exception as e:
        print(f"❌ Flow tool creation failed: {e}")
        import traceback
        traceback.print_exc()
        return None, None


def test_flow_tool_interface():
    """Test the flow tool interface (without actual execution)."""
    print("\n=== Testing Flow Tool Interface ===\n")
    
    generation_tool, status_tool = create_flow_tools()
    if not generation_tool:
        return
    
    # Test data
    test_product_id = str(uuid4())
    test_reference_url = "file:///path/to/test/image.jpg"
    test_product_info = {
        "product_id": test_product_id,
        "reference_url": test_reference_url,
        "product_name": "Test LED Product",
        "product_features": ["Blue LED", "USB Powered", "Portable"],
        "style_requirements": {"background": "white", "lighting": "soft"},
        "approval_threshold": 0.80
    }
    
    print("📋 Test configuration:")
    print(f"   - Product ID: {test_product_id}")
    print(f"   - Product Name: {test_product_info['product_name']}")
    print(f"   - Features: {len(test_product_info['product_features'])}")
    
    # Test status check
    print("\n📊 Testing status check:")
    status = status_tool._run(test_product_id)
    print(f"   - Status: {status.get('status')}")
    print(f"   - Message: {status.get('message')}")
    
    print("\n✅ Interface test completed")


def main():
    """Run all tests."""
    from dotenv import load_dotenv
    load_dotenv()
    
    settings = get_settings()
    print("🔧 Configuration:")
    print(f"   - OpenAI Model: {settings.openai_model}")
    print(f"   - API Key set: {bool(settings.openai_api_key)}")
    
    # Run tests
    test_flow_tool_creation()
    test_flow_tool_interface()
    
    print("\n✅ All tests completed!")


if __name__ == "__main__":
    main()