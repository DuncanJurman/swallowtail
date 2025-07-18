"""Image Generation Agent with CrewAI integration."""

from typing import Dict, Any, Optional

from crewai import Task

from ..agents.base import BaseAgent, AgentResult
from ..services.openai_image_service import OpenAIImageService, GenerationResult
from ..services.storage import SupabaseStorageService


class ImageGenerationAgent(BaseAgent):
    """CrewAI agent for generating product images."""
    
    def __init__(self):
        super().__init__(
            name="image_generation",
            role="Product Image Generator", 
            goal="Generate high-quality product images from references using gpt-image-1",
            backstory="""You are an expert product photographer AI specialized in creating 
            high-quality product images that match reference styles exactly. You use advanced 
            image generation to ensure products look professional and appealing.""",
            tools=[]
        )
        self.openai_service = OpenAIImageService()
        self.storage = SupabaseStorageService()
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Execute image generation task using CrewAI."""
        try:
            # Extract parameters from context
            reference_image_url = context.get('reference_image_url')
            product_name = context.get('product_name', 'Product')
            product_features = context.get('product_features', [])
            style_requirements = context.get('style_requirements', {})
            regenerate = context.get('regenerate', False)
            
            if not reference_image_url:
                return AgentResult(
                    success=False,
                    error="Reference image URL is required"
                )
            
            if regenerate:
                # Handle regeneration with feedback
                original_prompt = context.get('original_prompt', '')
                feedback = context.get('feedback', [])
                result = await self._regenerate_with_feedback(
                    reference_image_url,
                    original_prompt, 
                    feedback,
                    style_requirements
                )
            else:
                # Initial generation
                result = await self._generate_from_reference(
                    reference_image_url,
                    product_name,
                    product_features,
                    style_requirements
                )
            
            return AgentResult(
                success=True,
                data={
                    'image_data': result.image_data,
                    'prompt': result.prompt,
                    'product_name': product_name
                },
                metadata={
                    'reference_url': reference_image_url,
                    'regenerated': regenerate
                }
            )
            
        except Exception as e:
            self.log_error(f"Image generation failed: {str(e)}")
            return AgentResult(
                success=False,
                error=str(e)
            )
        
    async def _generate_from_reference(
        self,
        reference_image_url: str,
        product_name: str,
        product_features: list[str],
        style_requirements: Optional[Dict[str, str]] = None
    ) -> GenerationResult:
        """
        Generate product image from reference.
        
        Args:
            reference_image_url: URL of reference image
            product_name: Name of the product
            product_features: Key features to highlight
            style_requirements: Optional style requirements
            
        Returns:
            GenerationResult with generated image
        """
        # Download reference image
        reference_data = await self.storage.download_image(reference_image_url)
        
        # Prepare reference image
        reference_data = await self.openai_service.prepare_image(reference_data)
        
        # Build prompt
        prompt = self._build_prompt(product_name, product_features, style_requirements)
        
        # Generate image
        result = await self.openai_service.generate_image(
            reference_image=reference_data,
            prompt=prompt,
            size=style_requirements.get('size', '1024x1024') if style_requirements else '1024x1024',
            quality=style_requirements.get('quality', 'high') if style_requirements else 'high'
        )
        
        return result
    
    async def _regenerate_with_feedback(
        self,
        reference_image_url: str,
        original_prompt: str,
        feedback: list[str],
        style_requirements: Optional[Dict[str, str]] = None
    ) -> GenerationResult:
        """
        Regenerate image with feedback incorporated.
        
        Args:
            reference_image_url: URL of reference image
            original_prompt: Original prompt used
            feedback: List of improvements to make
            style_requirements: Optional style requirements
            
        Returns:
            GenerationResult with new image
        """
        # Download reference image
        reference_data = await self.storage.download_image(reference_image_url) 
        reference_data = await self.openai_service.prepare_image(reference_data)
        
        # Enhance prompt with feedback
        enhanced_prompt = self._enhance_prompt_with_feedback(original_prompt, feedback)
        
        # Generate new image
        result = await self.openai_service.generate_image(
            reference_image=reference_data,
            prompt=enhanced_prompt,
            size=style_requirements.get('size', '1024x1024') if style_requirements else '1024x1024',
            quality=style_requirements.get('quality', 'high') if style_requirements else 'high'
        )
        
        return result
        
    def _build_prompt(
        self,
        product_name: str,
        product_features: list[str],
        style_requirements: Optional[Dict[str, str]] = None
    ) -> str:
        """Build generation prompt."""
        prompt_parts = [
            f"Professional product photography of {product_name}.",
            f"Key features: {', '.join(product_features[:3])}." if product_features else "",
            "Style: Clean, modern, professional.",
            f"Background: {style_requirements.get('background', 'pure white')}." if style_requirements else "Background: pure white.",
            f"Lighting: {style_requirements.get('lighting', 'studio lighting with soft shadows')}." if style_requirements else "Lighting: studio lighting with soft shadows.",
            "High quality, sharp focus, match reference image style exactly."
        ]
        
        return " ".join(filter(None, prompt_parts))
        
    def _enhance_prompt_with_feedback(self, original_prompt: str, feedback: list[str]) -> str:
        """Add feedback to prompt."""
        if not feedback:
            return original_prompt
            
        enhanced = f"{original_prompt}\n\nIMPORTANT REQUIREMENTS:\n"
        for item in feedback[:5]:  # Limit to 5 items
            enhanced += f"- {item}\n"
            
        return enhanced
    
    def create_generation_task(
        self, 
        reference_url: str,
        product_name: str,
        features: list[str],
        style: Optional[Dict[str, str]] = None
    ) -> Task:
        """Create a CrewAI task for image generation."""
        description = f"""Generate a high-quality product image for {product_name}.
        
        Reference image: {reference_url}
        Key features to highlight: {', '.join(features)}
        Style requirements: {style or 'Standard product photography'}
        
        Use the gpt-image-1 model to create a professional product image that matches 
        the reference style exactly while highlighting the product features.
        """
        
        expected_output = """A high-quality product image that:
        1. Matches the reference image style
        2. Clearly shows all product features
        3. Has professional lighting and composition
        4. Is suitable for e-commerce use
        """
        
        return self.create_task(description, expected_output)