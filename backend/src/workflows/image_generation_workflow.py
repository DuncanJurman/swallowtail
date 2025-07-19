"""Image Generation Workflow using CrewAI."""

from typing import Dict, Any, Optional
from uuid import UUID
import asyncio
import logging

from crewai import Crew, Process

from ..crews.image_generation_crew import ImageGenerationCrew
from ..agents.image_generation import ImageGenerationAgent
from ..agents.image_evaluator import ImageEvaluatorAgent
from ..services.storage import SupabaseStorageService


logger = logging.getLogger(__name__)


class ImageGenerationWorkflow:
    """Orchestrates image generation and evaluation using CrewAI."""
    
    def __init__(self, max_attempts: int = 3):
        """Initialize workflow with agents."""
        self.max_attempts = max_attempts
        # These are still available for direct agent usage if needed
        self.generation_agent = ImageGenerationAgent()
        self.evaluator_agent = ImageEvaluatorAgent()
        self.storage = SupabaseStorageService()
        
    async def generate_product_image_with_crew(
        self,
        product_id: str,
        reference_image_url: str,
        product_name: str,
        product_features: list[str],
        style_requirements: Optional[Dict[str, str]] = None,
        approval_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        Generate product image using the new CrewAI-based implementation.
        
        This method uses the ImageGenerationCrew which handles the full
        generation and evaluation workflow with automatic retries.
        """
        # Convert product_id to UUID if it's a string
        if isinstance(product_id, str):
            product_uuid = UUID(product_id)
        else:
            product_uuid = product_id
            
        # Create and execute the crew
        crew = ImageGenerationCrew(
            product_id=product_uuid,
            reference_image_url=reference_image_url,
            product_name=product_name,
            product_features=product_features,
            style_requirements=style_requirements,
            approval_threshold=approval_threshold,
            max_attempts=self.max_attempts
        )
        
        return await crew.execute_async()
    
    async def generate_product_image(
        self,
        product_id: str,
        reference_image_url: str,
        product_name: str,
        product_features: list[str],
        style_requirements: Optional[Dict[str, str]] = None,
        approval_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        Generate and evaluate product image with automatic refinement.
        
        Args:
            product_id: Product identifier
            reference_image_url: URL of reference image
            product_name: Name of the product
            product_features: Key features to highlight
            style_requirements: Optional style requirements
            approval_threshold: Score threshold for approval
            
        Returns:
            Dict containing final result with image URL or error
        """
        attempt = 0
        current_feedback = []
        original_prompt = None
        
        while attempt < self.max_attempts:
            attempt += 1
            logger.info(f"Image generation attempt {attempt}/{self.max_attempts}")
            
            try:
                # Generate image
                if attempt == 1:
                    # Initial generation
                    gen_result = await self.generation_agent.execute({
                        'reference_image_url': reference_image_url,
                        'product_name': product_name,
                        'product_features': product_features,
                        'style_requirements': style_requirements,
                        'regenerate': False
                    })
                else:
                    # Regeneration with feedback
                    gen_result = await self.generation_agent.execute({
                        'reference_image_url': reference_image_url,
                        'original_prompt': original_prompt,
                        'feedback': current_feedback,
                        'style_requirements': style_requirements,
                        'regenerate': True
                    })
                
                if not gen_result.success:
                    logger.error(f"Generation failed: {gen_result.error}")
                    continue
                
                # Extract generation data
                image_data = gen_result.data['image_data']
                original_prompt = gen_result.data['prompt']
                
                # Evaluate generated image
                eval_result = await self.evaluator_agent.execute({
                    'reference_image_url': reference_image_url,
                    'generated_image_data': image_data,
                    'original_prompt': original_prompt,
                    'approval_threshold': approval_threshold
                })
                
                if not eval_result.success:
                    logger.error(f"Evaluation failed: {eval_result.error}")
                    continue
                
                # Log detailed scores if available
                if eval_result.metadata:
                    logger.info(f"Detailed evaluation scores - "
                              f"Visual: {eval_result.metadata.get('visual_fidelity_score')}%, "
                              f"Prompt: {eval_result.metadata.get('prompt_accuracy_score')}%, "
                              f"Technical: {eval_result.metadata.get('technical_quality_score')}%, "
                              f"Product: {eval_result.metadata.get('product_accuracy_score')}%")
                
                # Check if approved
                if eval_result.data['approved']:
                    logger.info(f"Image approved with overall score: {eval_result.data['score'] * 100:.1f}%")
                    
                    # Store approved image
                    image_url = await self.storage.upload_image(
                        image_data,
                        f"products/{product_id}/generated_{attempt}.png"
                    )
                    
                    # Include detailed scores in response if available
                    response = {
                        'success': True,
                        'image_url': image_url,
                        'score': eval_result.data['score'],
                        'attempts': attempt,
                        'prompt': original_prompt
                    }
                    
                    # Add detailed scores to response if available
                    if eval_result.metadata:
                        response['detailed_scores'] = {
                            'visual_fidelity': eval_result.metadata.get('visual_fidelity_score'),
                            'prompt_accuracy': eval_result.metadata.get('prompt_accuracy_score'),
                            'technical_quality': eval_result.metadata.get('technical_quality_score'),
                            'product_accuracy': eval_result.metadata.get('product_accuracy_score')
                        }
                    
                    return response
                
                # Not approved, update feedback for next attempt
                current_feedback = eval_result.data['feedback']
                logger.info(f"Image rejected with overall score: {eval_result.data['score'] * 100:.1f}%")
                logger.info(f"Feedback: {current_feedback}")
                
                # Log issues if available
                if eval_result.metadata and eval_result.metadata.get('issues'):
                    logger.info(f"Issues found: {eval_result.metadata['issues']}")
                
            except Exception as e:
                logger.error(f"Workflow error on attempt {attempt}: {str(e)}")
                
        # Max attempts reached without approval
        return {
            'success': False,
            'error': f"Failed to generate approved image after {self.max_attempts} attempts",
            'last_feedback': current_feedback,
            'attempts': self.max_attempts
        }
        
    async def generate_with_crew(
        self,
        product_id: str,
        reference_image_url: str,
        product_name: str,
        product_features: list[str],
        style_requirements: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        Alternative method using CrewAI task orchestration.
        
        This demonstrates how to use CrewAI's Crew for task coordination.
        """
        # Create generation task
        generation_task = self.generation_agent.create_generation_task(
            reference_url=reference_image_url,
            product_name=product_name,
            features=product_features,
            style=style_requirements
        )
        
        # Create evaluation task
        evaluation_task = self.evaluator_agent.create_evaluation_task(
            reference_url=reference_image_url,
            product_name=product_name,
            threshold=0.85
        )
        
        # Create crew
        crew = Crew(
            agents=[
                self.generation_agent.agent,
                self.evaluator_agent.agent
            ],
            tasks=[generation_task, evaluation_task],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute crew
        result = await asyncio.to_thread(
            crew.kickoff,
            inputs={
                'product_id': product_id,
                'reference_image_url': reference_image_url,
                'product_name': product_name,
                'product_features': ', '.join(product_features)
            }
        )
        
        return {
            'success': True,
            'crew_output': str(result),
            'product_id': product_id
        }