"""Image Evaluator Agent using multimodal LLM directly."""

from typing import List, Optional, Dict, Any
from crewai import Task

from ..agents.base import BaseAgent, AgentResult
from ..tools.image_storage_tool import ImageRetrievalTool


class ImageEvaluatorAgent(BaseAgent):
    """CrewAI agent for evaluating generated images using multimodal capabilities."""
    
    def __init__(self, **kwargs):
        """Initialize with configuration from YAML or kwargs."""
        # If no role is provided, load from YAML config
        if not kwargs.get('role'):
            # Load agent configuration from YAML
            from pathlib import Path
            import yaml
            
            config_path = Path(__file__).parent.parent / "config" / "agents.yaml"
            if config_path.exists():
                with open(config_path, 'r') as f:
                    agents_config = yaml.safe_load(f)
                    if 'image_evaluator' in agents_config:
                        agent_config = agents_config['image_evaluator']
                        kwargs.update({
                            'name': 'image_evaluator',
                            'role': agent_config.get('role', 'Visual Quality Inspector'),
                            'goal': agent_config.get('goal', 'Evaluate generated images for quality'),
                            'backstory': agent_config.get('backstory', 'You are an expert in visual quality assessment'),
                            'multimodal': agent_config.get('multimodal', True),
                            'reasoning': agent_config.get('reasoning', True),
                            'verbose': agent_config.get('verbose', True)
                        })
            else:
                # Fallback defaults if YAML not found
                kwargs.update({
                    'name': 'image_evaluator',
                    'role': 'Visual Quality Inspector',
                    'goal': 'Evaluate generated images for quality, accuracy, and alignment with requirements',
                    'backstory': 'You are an expert in visual quality assessment with years of experience.',
                    'multimodal': True,
                    'reasoning': True
                })
        
        # Add image retrieval tool for loading images to evaluate
        if 'tools' not in kwargs:
            kwargs['tools'] = [ImageRetrievalTool()]
        
        # Ensure multimodal is enabled for vision capabilities
        kwargs['multimodal'] = True
        
        super().__init__(**kwargs)
    
    def create_evaluation_task(
        self,
        reference_url: str,
        generated_url: str,
        product_name: str,
        original_prompt: str,
        threshold: float = 0.85
    ) -> Task:
        """Create a CrewAI task for image evaluation using multimodal LLM."""
        
        description = f"""Evaluate the quality of a generated product image for {product_name}.

Reference image: {reference_url}
Generated image: {generated_url}
Original prompt: {original_prompt}
Approval threshold: {threshold * 100}%

Your task:
1. Use the retrieve_image tool to load both the reference and generated images
2. As a multimodal agent, you can directly see and analyze both images
3. Compare the generated image against the reference for:
   - Visual fidelity (how well it matches the reference style)
   - Product accuracy (correct representation of product features)
   - Technical quality (sharpness, lighting, composition)
   - Prompt adherence (how well it follows the generation prompt)
   - E-commerce suitability (professional appearance, clear product visibility)

4. Provide detailed scores for each aspect (0-100)
5. Calculate an overall score based on weighted average
6. Determine if the image meets the approval threshold
7. If not approved, provide specific, actionable feedback for improvement

Remember: You have multimodal vision capabilities, so you can see and analyze the images directly.
Use your expertise to provide thorough, professional evaluation.
"""
        
        expected_output = """A comprehensive evaluation report containing:
1. Overall quality score (0-100)
2. Breakdown of scores:
   - Visual fidelity score
   - Product accuracy score  
   - Technical quality score
   - Prompt accuracy score
   - E-commerce suitability score
3. Approval decision (APPROVED/REJECTED) based on threshold
4. Detailed analysis of strengths and weaknesses
5. If rejected, specific improvement suggestions like:
   - "Increase brightness to match reference"
   - "Adjust angle to show product features better"
   - "Add more contrast to highlight details"
6. Confidence level in the evaluation
"""
        
        return self.create_task(description, expected_output)
    
    def create_feedback_task(
        self,
        image_url: str,
        previous_feedback: List[str],
        improvement_areas: List[str]
    ) -> Task:
        """Create a task to analyze if improvements were made based on feedback."""
        
        description = f"""Analyze if the regenerated image addresses previous feedback.

Image to evaluate: {image_url}
Previous feedback given:
{chr(10).join(f"- {fb}" for fb in previous_feedback)}

Areas that needed improvement:
{chr(10).join(f"- {area}" for area in improvement_areas)}

Your task:
1. Load and analyze the regenerated image
2. Check if each piece of feedback was addressed
3. Identify which improvements were successful
4. Note any remaining issues
5. Provide updated evaluation
"""
        
        expected_output = """A feedback analysis report with:
1. List of successfully addressed feedback items
2. List of unresolved issues
3. New issues introduced (if any)
4. Updated quality scores
5. Final recommendation
"""
        
        return self.create_task(description, expected_output)
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute method for compatibility with BaseAgent.
        
        Note: In the new architecture, agents work through CrewAI's task system
        and multimodal LLM capabilities, not through direct execution.
        """
        return AgentResult(
            success=True,
            data={
                "message": "This agent now evaluates images through multimodal LLM and CrewAI tasks"
            }
        )