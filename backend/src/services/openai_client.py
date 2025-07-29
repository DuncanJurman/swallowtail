"""OpenAI client for image generation using images.edit endpoint with gpt-image-1."""

import base64
import io
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4

from openai import AsyncOpenAI
from PIL import Image

from src.core.config import get_settings


@dataclass
class ImageGenerationResult:
    """Result from image generation attempt."""
    attempt_id: str
    prompt_used: str
    image_data: bytes
    metadata: Dict[str, Any] = None
    created_at: datetime = None
    quality_settings: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}


class OpenAIImageClient:
    """Client for OpenAI images.edit endpoint with gpt-image-1 model."""
    
    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        self.model = "gpt-image-1"
        
    async def generate_from_reference(
        self,
        reference_images: List[bytes],
        prompt: str,
        size: str = "1024x1024"
    ) -> ImageGenerationResult:
        """
        Generate image based on reference images and prompt.
        
        Args:
            reference_images: List of reference images in bytes
            prompt: Text prompt describing desired output
            size: Image size (1024x1024, 1536x1024, 1024x1536)
            
        Returns:
            ImageGenerationResult with generated image data
        """
        # Prepare image files
        image_files = []
        for img_data in reference_images:
            img_file = io.BytesIO(img_data)
            image_files.append(img_file)
        
        try:
            # Call OpenAI API with gpt-image-1
            response = await self.client.images.edit(
                model=self.model,
                image=image_files,
                prompt=prompt,
                size=size,
                response_format="b64_json"
            )
            
            # Extract image data
            image_b64 = response.data[0].b64_json
            image_data = base64.b64decode(image_b64)
            
            # Generate unique ID
            attempt_id = str(uuid4())
            
            return ImageGenerationResult(
                attempt_id=attempt_id,
                prompt_used=prompt,
                image_data=image_data,
                metadata={
                    "model": self.model,
                    "size": size,
                    "reference_count": len(reference_images)
                },
                quality_settings={
                    "size": size
                }
            )
            
        finally:
            # Clean up file objects
            for f in image_files:
                f.close()
            
    async def generate_from_single_reference(
        self,
        reference_image: bytes,
        prompt: str,
        size: str = "1024x1024"
    ) -> ImageGenerationResult:
        """
        Convenience method for single reference image.
        
        Args:
            reference_image: Reference image in bytes
            prompt: Text prompt describing desired output
            size: Image size
            
        Returns:
            ImageGenerationResult with generated image data
        """
        return await self.generate_from_reference(
            reference_images=[reference_image],
            prompt=prompt,
            size=size
        )
            
    async def prepare_reference_image(self, image_data: bytes, max_size_mb: int = 4) -> bytes:
        """
        Prepare reference image for API (resize if needed, convert format).
        
        Args:
            image_data: Original image data
            max_size_mb: Maximum size in MB (default 4MB)
            
        Returns:
            Processed image data ready for API
        """
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if necessary
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')
            
        # Check file size
        max_size_bytes = max_size_mb * 1024 * 1024
        
        output = io.BytesIO()
        img.save(output, format='PNG', optimize=True)
        
        # If image is too large, resize it
        if output.tell() > max_size_bytes:
            # Calculate resize ratio
            current_size = output.tell()
            ratio = (max_size_bytes / current_size) ** 0.5
            
            new_width = int(img.width * ratio * 0.9)  # 0.9 for safety margin
            new_height = int(img.height * ratio * 0.9)
            
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Save resized image
            output = io.BytesIO()
            img.save(output, format='PNG', optimize=True)
        
        output.seek(0)
        return output.read()