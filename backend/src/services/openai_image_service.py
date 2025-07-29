"""Simplified OpenAI service for image generation and analysis."""

import base64
import io
from typing import List
from dataclasses import dataclass

from openai import AsyncOpenAI
from PIL import Image
from pydantic import BaseModel, Field

from src.core.config import get_settings


@dataclass
class GenerationResult:
    """Simple result from image generation."""
    image_data: bytes
    prompt: str
    

@dataclass 
class EvaluationResult:
    """Simple evaluation result."""
    approved: bool
    score: float
    feedback: List[str]
    metadata: dict = None


class ImageEvaluationResponse(BaseModel):
    """Structured response for image evaluation using Pydantic."""
    overall_score: int = Field(description="Overall quality score from 0-100")
    visual_fidelity_score: int = Field(description="How well it matches the reference (0-100)")
    prompt_accuracy_score: int = Field(description="How well it follows the prompt (0-100)")
    technical_quality_score: int = Field(description="Sharpness, lighting, composition (0-100)")
    product_accuracy_score: int = Field(description="Product detail accuracy (0-100)")
    issues: List[str] = Field(description="List of issues found, or empty list if none")
    improvements: List[str] = Field(description="List of suggested improvements, or empty list if none")
    

class OpenAIImageService:
    """Simple service for OpenAI image operations."""
    
    def __init__(self):
        settings = get_settings()
        self.client = AsyncOpenAI(api_key=settings.openai_api_key)
        
    async def generate_image(
        self,
        reference_image: bytes,
        prompt: str,
        size: str = "1024x1024"
    ) -> GenerationResult:
        """
        Generate image from reference using gpt-image-1.
        
        Args:
            reference_image: Reference image bytes
            prompt: Generation prompt
            size: Output size
            
        Returns:
            GenerationResult with image data
        """
        # Prepare reference image with proper file naming
        image_file = io.BytesIO(reference_image)
        image_file.name = "image.png"  # Set a name so OpenAI can determine the mime type
        
        try:
            # Call images.edit endpoint
            response = await self.client.images.edit(
                model="gpt-image-1",
                image=image_file,
                prompt=prompt,
                size=size
            )
            
            # Get image data
            # The response might have URL or b64_json depending on the format
            if hasattr(response.data[0], 'b64_json') and response.data[0].b64_json:
                image_b64 = response.data[0].b64_json
                image_data = base64.b64decode(image_b64)
            elif hasattr(response.data[0], 'url') and response.data[0].url:
                # Download from URL
                import httpx
                async with httpx.AsyncClient() as client:
                    img_response = await client.get(response.data[0].url)
                    image_data = img_response.content
            else:
                raise ValueError("No image data in response")
            
            return GenerationResult(
                image_data=image_data,
                prompt=prompt
            )
            
        finally:
            image_file.close()
            
    async def evaluate_images(
        self,
        reference_image: bytes,
        generated_image: bytes,
        original_prompt: str,
        approval_threshold: float = 0.85
    ) -> EvaluationResult:
        """
        Evaluate generated image against reference using structured output.
        
        This method uses OpenAI's structured output feature with Pydantic models
        to ensure consistent, type-safe evaluation results. The evaluation includes
        detailed scores for visual fidelity, prompt accuracy, technical quality,
        and product accuracy.
        
        Args:
            reference_image: Reference image bytes
            generated_image: Generated image bytes  
            original_prompt: The prompt used for generation
            approval_threshold: Score threshold for approval
            
        Returns:
            EvaluationResult with approval decision, score, feedback, and detailed metadata
        """
        # Convert images to base64
        ref_b64 = base64.b64encode(reference_image).decode('utf-8')
        gen_b64 = base64.b64encode(generated_image).decode('utf-8')
        
        # Create evaluation prompt for structured output
        eval_prompt = f"""You are an expert image quality evaluator. Compare these two product images and evaluate the generated image quality.

Reference image (first): The target style and quality to match
Generated image (second): Created with prompt: "{original_prompt}"

Carefully analyze both images and provide scores for each aspect. Be specific about any issues or improvements needed."""

        # Call GPT-4 vision with structured output
        completion = await self.client.chat.completions.parse(
            model="gpt-4o-2024-08-06",  # Using model that supports structured outputs
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert at evaluating product image quality."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": eval_prompt},
                        {
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{ref_b64}"}
                        },
                        {
                            "type": "image_url", 
                            "image_url": {"url": f"data:image/png;base64,{gen_b64}"}
                        }
                    ]
                }
            ],
            response_format=ImageEvaluationResponse,
            max_tokens=500
        )
        
        # Get parsed response
        message = completion.choices[0].message
        if not message.parsed:
            raise ValueError("Failed to get structured response from evaluation")
            
        eval_response = message.parsed
        
        # Convert to our result format
        score = eval_response.overall_score / 100.0
        feedback = eval_response.improvements
        
        return EvaluationResult(
            approved=score >= approval_threshold,
            score=score,
            feedback=feedback,
            # Store the full structured response for debugging
            metadata={
                'visual_fidelity_score': eval_response.visual_fidelity_score,
                'prompt_accuracy_score': eval_response.prompt_accuracy_score,
                'technical_quality_score': eval_response.technical_quality_score,
                'product_accuracy_score': eval_response.product_accuracy_score,
                'issues': eval_response.issues
            }
        )
        
    async def prepare_image(self, image_data: bytes, max_size_mb: int = 4) -> bytes:
        """Prepare image for API (resize if needed)."""
        img = Image.open(io.BytesIO(image_data))
        
        # Convert to RGB if needed
        if img.mode not in ('RGB', 'RGBA'):
            img = img.convert('RGB')
            
        # Check size
        output = io.BytesIO()
        img.save(output, format='PNG', optimize=True)
        
        # Resize if too large
        if output.tell() > max_size_mb * 1024 * 1024:
            # Resize to fit
            ratio = ((max_size_mb * 1024 * 1024) / output.tell()) ** 0.5
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            output = io.BytesIO()
            img.save(output, format='PNG', optimize=True)
            
        output.seek(0)
        return output.read()
    
    # Synchronous wrapper methods for testing
    def prepare_image_sync(self, image_data: bytes, max_size_mb: int = 4) -> bytes:
        """Synchronous wrapper for prepare_image."""
        import asyncio
        return asyncio.run(self.prepare_image(image_data, max_size_mb))
    
    def generate_image_sync(
        self,
        reference_image: bytes,
        prompt: str,
        size: str = "1024x1024"
    ) -> GenerationResult:
        """Synchronous wrapper for generate_image."""
        import asyncio
        return asyncio.run(self.generate_image(reference_image, prompt, size))