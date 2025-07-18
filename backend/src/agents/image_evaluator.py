"""Image Evaluator Agent with CrewAI integration."""

from typing import Dict, Any

from crewai import Task

from ..agents.base import BaseAgent, AgentResult
from ..services.openai_image_service import OpenAIImageService, EvaluationResult
from ..services.storage import SupabaseStorageService


class ImageEvaluatorAgent(BaseAgent):
    """CrewAI agent for evaluating generated images."""
    
    def __init__(self):
        super().__init__(
            name="image_evaluator",
            role="Product Image Quality Evaluator",
            goal="Ensure generated images match reference quality using gpt-4.1 vision analysis",
            backstory="""You are an expert visual quality control specialist with deep knowledge 
            of product photography standards. You meticulously compare generated images against 
            references to ensure they meet high quality standards for e-commerce use.""",
            tools=[]
        )
        self.openai_service = OpenAIImageService()
        self.storage = SupabaseStorageService()
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Execute image evaluation task using CrewAI."""
        try:
            # Extract parameters from context
            reference_image_url = context.get('reference_image_url')
            generated_image_data = context.get('generated_image_data')
            original_prompt = context.get('original_prompt', '')
            approval_threshold = context.get('approval_threshold', 0.85)
            
            if not reference_image_url or not generated_image_data:
                return AgentResult(
                    success=False,
                    error="Both reference image URL and generated image data are required"
                )
            
            # Perform evaluation
            result = await self._evaluate_generated_image(
                reference_image_url,
                generated_image_data,
                original_prompt,
                approval_threshold
            )
            
            # Include detailed scores in metadata if available
            agent_metadata = {
                'threshold': approval_threshold,
                'prompt': original_prompt
            }
            
            # Add detailed scores from structured evaluation if present
            if result.metadata:
                agent_metadata.update({
                    'visual_fidelity_score': result.metadata.get('visual_fidelity_score'),
                    'prompt_accuracy_score': result.metadata.get('prompt_accuracy_score'),
                    'technical_quality_score': result.metadata.get('technical_quality_score'),
                    'product_accuracy_score': result.metadata.get('product_accuracy_score'),
                    'issues': result.metadata.get('issues', [])
                })
            
            return AgentResult(
                success=True,
                data={
                    'approved': result.approved,
                    'score': result.score,
                    'feedback': result.feedback
                },
                metadata=agent_metadata
            )
            
        except Exception as e:
            self.log_error(f"Image evaluation failed: {str(e)}")
            return AgentResult(
                success=False,
                error=str(e)
            )
    
    async def _evaluate_generated_image(
        self,
        reference_image_url: str,
        generated_image_data: bytes,
        original_prompt: str,
        approval_threshold: float = 0.85
    ) -> EvaluationResult:
        """
        Evaluate generated image against reference.
        
        Args:
            reference_image_url: URL of reference image
            generated_image_data: Generated image bytes
            original_prompt: Prompt used for generation
            approval_threshold: Score threshold for approval (0-1)
            
        Returns:
            EvaluationResult with approval decision and feedback
        """
        # Download reference image
        reference_data = await self.storage.download_image(reference_image_url)
        
        # Evaluate using GPT-4 vision
        result = await self.openai_service.evaluate_images(
            reference_image=reference_data,
            generated_image=generated_image_data,
            original_prompt=original_prompt,
            approval_threshold=approval_threshold
        )
        
        return result
    
    def create_evaluation_task(
        self,
        reference_url: str,
        product_name: str,
        threshold: float = 0.85
    ) -> Task:
        """Create a CrewAI task for image evaluation."""
        description = f"""Evaluate the quality of a generated product image for {product_name}.
        
        Compare the generated image against the reference image at: {reference_url}
        
        Assess:
        1. Visual fidelity to the reference style
        2. Product accuracy and feature visibility
        3. Technical quality (sharpness, lighting, composition)
        4. Suitability for e-commerce use
        
        Approval threshold: {threshold * 100}%
        
        If the image doesn't meet standards, provide specific improvements for the prompt.
        """
        
        expected_output = """An evaluation report containing:
        1. Overall quality score (0-100%)
        2. Approval decision (approved/rejected)
        3. Specific feedback on any issues found
        4. Concrete prompt improvements if needed
        """
        
        return self.create_task(description, expected_output)