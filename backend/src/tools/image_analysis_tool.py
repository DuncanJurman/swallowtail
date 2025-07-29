"""Image Analysis Tool for CrewAI agents to understand images."""

from typing import Any, Dict, Type
from crewai.tools import BaseTool
from pydantic import BaseModel, Field
import base64
import os

from openai import OpenAI
from ..core.config import get_settings


class ImageAnalysisInput(BaseModel):
    """Input schema for image analysis."""
    image_path: str = Field(
        description="Path to the image file to analyze"
    )
    analysis_focus: str = Field(
        default="product photography",
        description="What to focus on in the analysis (e.g., 'product photography', 'style and composition', 'lighting and color')"
    )


class ImageAnalysisTool(BaseTool):
    """Tool for analyzing images using multimodal LLM."""
    
    name: str = "analyze_image"
    description: str = """Analyze an image to understand its visual elements, style, composition, and details.
    Use this tool to understand reference images before generating new ones."""
    args_schema: Type[BaseModel] = ImageAnalysisInput
    
    def _run(
        self,
        image_path: str,
        analysis_focus: str = "product photography"
    ) -> Dict[str, Any]:
        """Analyze an image and return a detailed description."""
        try:
            # Get OpenAI client
            settings = get_settings()
            client = OpenAI(api_key=settings.openai_api_key)
            # Verify file exists
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "error": f"Image file not found: {image_path}"
                }
            
            # Load and encode image
            with open(image_path, 'rb') as f:
                image_data = f.read()
            
            base64_image = base64.b64encode(image_data).decode('utf-8')
            
            # Create analysis prompt based on focus
            if analysis_focus == "product photography":
                prompt = """Analyze this product image and describe:
1. Product details (what is shown, key features visible)
2. Lighting setup (type, direction, color temperature, intensity)
3. Background and setting (environment, props, context)
4. Composition (framing, angles, focal points)
5. Color palette and mood
6. Photography style (studio, lifestyle, etc.)
7. Any special effects or post-processing visible

Be specific and detailed to help recreate a similar style."""
            else:
                prompt = f"Analyze this image focusing on {analysis_focus}. Provide detailed observations."
            
            # Call GPT-4 Vision
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/jpeg;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=1000
            )
            
            analysis = response.choices[0].message.content
            
            return {
                "success": True,
                "analysis": analysis,
                "image_path": image_path,
                "focus": analysis_focus,
                "message": "Image analyzed successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "image_path": image_path
            }