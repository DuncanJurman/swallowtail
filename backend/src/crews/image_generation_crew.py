"""Image Generation Crew using proper CrewAI architecture."""

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task, before_kickoff

from ..tools.image_generation_tool import ImageGenerationTool
from ..tools.image_storage_tool import ImageStorageTool
from ..core.config import get_settings


@CrewBase
class ImageGenerationCrew():
    """Crew for generating and evaluating product images using CrewAI properly."""
    
    # YAML config paths relative to this file
    agents_config = '../config/agents.yaml'
    tasks_config = '../config/tasks.yaml'
    
    def __init__(
        self,
        product_id: UUID,
        reference_image_url: str,
        product_name: str,
        product_features: List[str],
        style_requirements: Optional[Dict[str, str]] = None,
        previous_feedback: Optional[List[Dict[str, Any]]] = None
    ):
        """Initialize with image generation parameters."""
        self.settings = get_settings()
        self.product_id = product_id
        self.reference_image_url = reference_image_url
        self.product_name = product_name
        self.product_features = product_features
        self.style_requirements = style_requirements or {}
        self.previous_feedback = previous_feedback or []
        self.logger = logging.getLogger(f"ImageGenerationCrew[{product_id}]")
        
        # Initialize tools
        self.generation_tool = ImageGenerationTool()
        self.storage_tool = ImageStorageTool()
    
    @before_kickoff
    def prepare_crew(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare inputs before crew execution."""
        self.logger.info(f"Starting image generation for {self.product_name}")
        inputs['timestamp'] = datetime.now(timezone.utc).isoformat()
        return inputs
    
    @agent
    def image_generator(self) -> Agent:
        """Image generation specialist with tools."""
        # Create LLM for image generation
        llm = LLM(
            model=self.settings.openai_model,
            temperature=0.7,
            max_tokens=4000
        )
        
        return Agent(
            config=self.agents_config['image_generator'],  # type: ignore[index]
            llm=llm,
            tools=[self.generation_tool, self.storage_tool],
            verbose=True,
            multimodal=True,  # Enable multimodal capabilities
            max_execution_time=300,  # 5 minute timeout
            max_iter=10  # Limit iterations to prevent infinite loops
        )
    
    
    @task
    def generate_image_task(self) -> Task:
        """Task to generate product image."""
        # Build comprehensive task description
        features_str = "\n".join(f"- {feature}" for feature in self.product_features)
        
        style_desc = ""
        if self.style_requirements:
            style_parts = []
            for key, value in self.style_requirements.items():
                style_parts.append(f"{key.capitalize()}: {value}")
            style_desc = "\n" + "\n".join(style_parts)
        
        # Add feedback context if available
        feedback_desc = ""
        if self.previous_feedback:
            feedback_desc = "\n\nPREVIOUS FEEDBACK TO ADDRESS:"
            for fb in self.previous_feedback:
                feedback_desc += f"\n- Attempt {fb.get('attempt', '?')}: {fb.get('feedback', '')}"
        
        return Task(
            description=f"""Generate a high-quality product image for {self.product_name}.

Reference image is available at: {self.reference_image_url}
You can see and analyze this image directly with your multimodal capabilities.

Key features to highlight:
{features_str}
{style_desc}{feedback_desc}

Steps:
1. Examine the reference image to understand its style, composition, lighting, and mood
2. {f'Consider the previous feedback and adjust your approach accordingly' if self.previous_feedback else 'Create a detailed prompt that captures the reference style while highlighting product features'}
3. Use the generate_image tool with the reference image path and your crafted prompt
4. The tool will return a temporary file path for the generated image
5. Store the final image using the store_image tool with product_id: {str(self.product_id)}

Focus on creating an image that:
- Matches the reference image's style and quality
- Clearly showcases all product features
- Has professional lighting and composition
- Is suitable for e-commerce use{f' and addresses the previous feedback' if self.previous_feedback else ''}""",
            expected_output="""A successfully generated and stored product image with:
1. URL of the stored image (from Supabase storage)
2. The prompt used for generation
3. Temporary file path of the generated image
4. Confirmation that the image matches requirements""",
            agent=self.image_generator()
        )
    
    
    @crew
    def crew(self) -> Crew:
        """Create the image generation crew."""
        return Crew(
            agents=self.agents,  # Automatically includes all @agent methods
            tasks=self.tasks,    # Automatically includes all @task methods
            process=Process.sequential,
            verbose=True,
            memory=True,
            planning=True,
            planning_llm=LLM(
                model=self.settings.openai_model,
                temperature=0.5
            ),
            output_log_file="output/crew_logs.json",  # Save detailed logs
            max_rpm=10,  # Rate limiting to prevent API overload
            step_callback=self._log_step  # Log each step
        )
    
    def _log_step(self, agent_output):
        """Callback to log each agent step."""
        self.logger.info(f"Agent step completed: {agent_output}")
        return agent_output
    
    async def execute_async(self) -> Dict[str, Any]:
        """Execute the crew asynchronously."""
        self.logger.info(f"Starting image generation for {self.product_name}")
        
        inputs = {
            "product_id": str(self.product_id),
            "reference_image_url": self.reference_image_url,
            "product_name": self.product_name,
            "product_features": self.product_features,
            "style_requirements": self.style_requirements,
            "previous_feedback": self.previous_feedback
        }
        
        try:
            result = self.crew().kickoff(inputs=inputs)
            
            # Parse the result
            if hasattr(result, 'raw'):
                output = result.raw
            else:
                output = str(result)
            
            # Extract useful information from output
            temp_path = None
            storage_url = None
            prompt_used = None
            
            # Parse temp file path from output
            import re
            # Look for common temp file patterns
            temp_patterns = [
                r'Temporary file path[:\s]+([^\s]+\.png)',
                r'temp_image_path[:\s]+([^\s]+\.png)',
                r'/tmp/[^\s]+\.png',
                r'/var/folders/[^\s]+\.png'
            ]
            
            for pattern in temp_patterns:
                match = re.search(pattern, output)
                if match:
                    temp_path = match.group(1) if '(' in pattern else match.group(0)
                    break
            
            if "url" in output and "storage" in output:
                url_match = re.search(r'url["\s:]+([^\s",]+)', output)
                if url_match:
                    storage_url = url_match.group(1)
            
            # Extract prompt used
            prompt_patterns = [
                r'Prompt used for generation:\s*"([^"]+)"',
                r'prompt:\s*"([^"]+)"',
                r'"([^"]{50,})"'  # Any long quoted string likely to be the prompt
            ]
            
            for pattern in prompt_patterns:
                match = re.search(pattern, output, re.IGNORECASE | re.DOTALL)
                if match:
                    prompt_used = match.group(1)
                    break
            
            return {
                "success": True,
                "output": output,
                "temp_image_path": temp_path,
                "storage_url": storage_url,
                "prompt_used": prompt_used,
                "product_id": str(self.product_id),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            self.logger.error(f"Image generation failed: {str(e)}")
            return {
                "success": False,
                "error": str(e),
                "product_id": str(self.product_id)
            }