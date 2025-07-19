"""Direct test of ImageGenerationTool without full crew orchestration."""
import os
import pytest
from pathlib import Path
from datetime import datetime
import shutil
from dotenv import load_dotenv

# Load environment
load_dotenv()

from src.tools.image_generation_tool import ImageGenerationTool


class TestImageToolDirect:
    """Test the ImageGenerationTool directly for faster validation."""
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for integration testing"
    )
    @pytest.mark.timeout(60)  # 1 minute timeout
    def test_direct_image_generation(self):
        """Test direct image generation with the tool."""
        # Setup
        reference_image_path = Path(__file__).parent.parent / "reference_images" / "led-squirtle.jpg"
        assert reference_image_path.exists(), f"Reference image not found at {reference_image_path}"
        
        # Create tool
        tool = ImageGenerationTool()
        
        # Generate image with specific prompt
        prompt = """A high-quality product image of a Squirtle Pokemon LED night light 
        placed on a modern dorm room nightstand at night. The blue LED glow softly 
        illuminates the room, creating a cozy nighttime atmosphere. Professional 
        e-commerce style photo with sharp details and balanced lighting."""
        
        print(f"\n🚀 Testing direct tool execution...")
        print(f"📸 Reference image: {reference_image_path}")
        print(f"📝 Prompt: {prompt[:100]}...")
        
        # Run the tool
        result = tool._run(
            reference_image_path=f"file://{reference_image_path.absolute()}",
            prompt=prompt,
            size="1024x1024"
        )
        
        # Validate result
        assert result["success"], f"Tool execution failed: {result.get('error', 'Unknown error')}"
        assert result.get("temp_image_path"), "No image path returned"
        assert result["format"] == "png"
        assert result["size"] == "1024x1024"
        
        # Verify image exists and is valid
        temp_path = result["temp_image_path"]
        assert os.path.exists(temp_path), f"Generated image not found at {temp_path}"
        
        file_size = os.path.getsize(temp_path)
        assert file_size > 10000, f"Generated image too small: {file_size} bytes"
        print(f"✅ Image generated: {temp_path} ({file_size:,} bytes)")
        
        # Save to output directory
        output_dir = Path("output/generated_images")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = output_dir / f"tool_direct_led_squirtle_{timestamp}.png"
        
        shutil.copy2(temp_path, output_path)
        print(f"✅ Image saved to: {output_path}")
        
        # Cleanup
        os.remove(temp_path)
        print("✅ Temporary file cleaned up")
        
        # Return the output path for inspection
        return str(output_path)
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for integration testing"
    )
    @pytest.mark.timeout(60)
    def test_tool_with_different_sizes(self):
        """Test image generation with different sizes."""
        reference_image_path = Path(__file__).parent.parent / "reference_images" / "led-squirtle.jpg"
        assert reference_image_path.exists()
        
        tool = ImageGenerationTool()
        sizes = ["512x512", "1024x1024"]
        
        output_dir = Path("output/generated_images")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for size in sizes:
            print(f"\n🎨 Testing size: {size}")
            
            result = tool._run(
                reference_image_path=f"file://{reference_image_path.absolute()}",
                prompt=f"LED Squirtle night light product photo, {size} resolution",
                size=size
            )
            
            assert result["success"], f"Failed for size {size}: {result.get('error')}"
            assert result["size"] == size
            
            # Save with size in filename
            temp_path = result["temp_image_path"]
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_path = output_dir / f"tool_test_{size.replace('x', '_')}_{timestamp}.png"
            
            shutil.copy2(temp_path, output_path)
            print(f"✅ {size} image saved to: {output_path}")
            
            # Cleanup
            os.remove(temp_path)
    
    @pytest.mark.integration
    @pytest.mark.skipif(
        not os.getenv("OPENAI_API_KEY"),
        reason="Requires OPENAI_API_KEY for integration testing"
    )
    def test_tool_error_handling(self):
        """Test tool handles errors gracefully."""
        tool = ImageGenerationTool()
        
        # Test with non-existent file
        result = tool._run(
            reference_image_path="/nonexistent/file.jpg",
            prompt="Test prompt"
        )
        
        assert not result["success"]
        assert "error" in result
        print(f"✅ Error handled correctly: {result['error']}")