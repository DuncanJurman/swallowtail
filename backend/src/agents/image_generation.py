"""Image Generation Agent using CrewAI properly."""

from typing import Dict, Any, List, Optional
from crewai import Task

from ..agents.base import BaseAgent, AgentResult
from ..tools.image_generation_tool import ImageGenerationTool
from ..tools.image_storage_tool import ImageStorageTool, ImageRetrievalTool


class ImageGenerationAgent(BaseAgent):
    """CrewAI agent for coordinating product image generation."""
    
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
                    if 'image_generator' in agents_config:
                        agent_config = agents_config['image_generator']
                        kwargs.update({
                            'name': 'image_generator',
                            'role': agent_config.get('role', 'Product Image Specialist'),
                            'goal': agent_config.get('goal', 'Generate high-quality product images'),
                            'backstory': agent_config.get('backstory', 'You are a professional product photographer'),
                            'multimodal': agent_config.get('multimodal', True),
                            'max_iter': agent_config.get('max_iter', 15),
                            'verbose': agent_config.get('verbose', True)
                        })
            else:
                # Fallback defaults if YAML not found
                kwargs.update({
                    'name': 'image_generator',
                    'role': 'Product Image Specialist',
                    'goal': 'Generate high-quality product images that match brand standards and reference styles',
                    'backstory': 'You are a professional product photographer and image generation expert.'
                })
        
        # Add tools for image generation
        if 'tools' not in kwargs:
            kwargs['tools'] = [
                ImageGenerationTool(),
                ImageStorageTool(),
                ImageRetrievalTool()
            ]
        
        super().__init__(**kwargs)
    
    def create_generation_task(
        self,
        reference_url: str,
        product_name: str,
        features: List[str],
        style: Optional[Dict[str, str]] = None
    ) -> Task:
        """Create a CrewAI task for image generation."""
        # Build a comprehensive description for the task
        style_desc = ""
        if style:
            style_parts = []
            if 'background' in style:
                style_parts.append(f"Background: {style['background']}")
            if 'lighting' in style:
                style_parts.append(f"Lighting: {style['lighting']}")
            if 'atmosphere' in style:
                style_parts.append(f"Atmosphere: {style['atmosphere']}")
            style_desc = "\n".join(style_parts)
        
        description = f"""Generate a high-quality product image for {product_name}.

Reference image: {reference_url}
Key features to highlight:
{chr(10).join(f"- {feature}" for feature in features)}

{style_desc}

Steps:
1. First, retrieve and analyze the reference image using the retrieve_image tool
2. Understand the product's key features and how to best showcase them
3. Create a detailed prompt that captures the essence of the reference style while highlighting the product features
4. Use the generate_image tool to create the product image
5. Review the generated image to ensure it meets quality standards
6. If satisfied, store the image using the store_image tool

Focus on creating an image that:
- Matches the reference image's style and quality
- Clearly showcases all product features
- Has professional lighting and composition
- Is suitable for e-commerce use
"""
        
        expected_output = """A successfully generated and stored product image with:
1. URL of the stored image
2. The prompt used for generation
3. Confirmation that the image matches requirements
4. Any relevant metadata about the generation process
"""
        
        return self.create_task(description, expected_output)
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute method for compatibility with BaseAgent.
        
        Note: In the new architecture, agents work through CrewAI's task system,
        not through direct execution. This method is here for compatibility only.
        """
        return AgentResult(
            success=True,
            data={
                "message": "This agent now works through CrewAI tasks and tools"
            }
        )