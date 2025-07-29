"""Image Generation Tool for CrewAI agents."""

from typing import Any, Dict, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from ..services.openai_image_service import OpenAIImageService, GenerationResult


class ImageGenerationInput(BaseModel):
    """Input schema for image generation."""
    reference_image_path: str = Field(
        description="Path or URL to the reference image"
    )
    prompt: str = Field(
        description="Detailed prompt describing the desired image"
    )
    size: str = Field(
        default="1024x1024",
        description="Image size (1024x1024, 512x512, or 256x256)"
    )


class ImageGenerationTool(BaseTool):
    """Tool for generating images using OpenAI's API."""
    
    name: str = "generate_image"
    description: str = """Generate a product image based on a reference image and prompt.
    This tool uses OpenAI's image generation API to create high-quality product images
    that match the style of a reference image while following the provided prompt."""
    args_schema: Type[BaseModel] = ImageGenerationInput
    
    def __init__(self):
        super().__init__()
        self._service = OpenAIImageService()
    
    def _run(
        self,
        reference_image_path: str,
        prompt: str,
        size: str = "1024x1024"
    ) -> Dict[str, Any]:
        """
        Generate an image synchronously.
        
        Args:
            reference_image_path: Path or URL to reference image
            prompt: Generation prompt
            size: Image size
            
        Returns:
            Dict with temp_image_path, prompt, and success status
        """
        import asyncio
        import httpx
        import tempfile
        
        try:
            # Load reference image
            if reference_image_path.startswith("file://"):
                file_path = reference_image_path.replace("file://", "")
                with open(file_path, 'rb') as f:
                    reference_data = f.read()
            elif reference_image_path.startswith("/"):
                # Local file path
                with open(reference_image_path, 'rb') as f:
                    reference_data = f.read()
            else:
                # URL - download it synchronously
                response = httpx.get(reference_image_path)
                reference_data = response.content
            
            # Run async operations in a new event loop
            async def _async_operations():
                # Prepare the image
                prepared_image = await self._service.prepare_image(reference_data)
                
                # Generate the image
                result = await self._service.generate_image(
                    reference_image=prepared_image,
                    prompt=prompt,
                    size=size
                )
                return result
            
            # Execute async operations - handle existing event loop
            try:
                asyncio.get_running_loop()
                # We're already in an event loop, use nest_asyncio
                import nest_asyncio
                nest_asyncio.apply()
                result = asyncio.run(_async_operations())
            except RuntimeError:
                # No event loop running, create one normally
                result = asyncio.run(_async_operations())
            
            # Save image to temporary file for other tools to use
            # Create temporary file
            with tempfile.NamedTemporaryFile(mode='wb', suffix='.png', delete=False) as f:
                f.write(result.image_data)
                temp_path = f.name
            
            return {
                "success": True,
                "temp_image_path": temp_path,
                "prompt": result.prompt,
                "size": size,
                "format": "png",
                "message": f"Successfully generated image and saved to: {temp_path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "prompt": prompt
            }