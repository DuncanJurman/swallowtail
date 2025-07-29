"""Tools for integrating CrewAI Flows with agents."""

import logging
from typing import Dict, Any, Optional
from uuid import UUID
from pydantic import BaseModel, Field

from crewai.tools import BaseTool

from ..flows.image_generation_flow import ImageGenerationFlow


class ImageGenerationFlowTool(BaseTool):
    """Tool that allows agents to use the ImageGenerationFlow."""
    
    name: str = "image_generation_flow"
    description: str = """
    Generate high-quality product images using an automated workflow.
    
    This tool manages the entire image generation process including:
    - Generating initial product images from reference images
    - Automatic quality evaluation
    - Iterative improvement based on feedback
    - Storage of approved images
    
    Input should include:
    - product_id: UUID of the product
    - reference_url: URL or path to reference image
    - product_name: Name of the product
    - product_features: List of key product features
    - style_requirements: Dictionary of style preferences (optional)
    - approval_threshold: Quality threshold for approval (0-1, default 0.85)
    """
    
    # Store flow instances as a class variable
    _flow_instances: Dict[UUID, ImageGenerationFlow] = {}
    
    @property
    def logger(self):
        """Get logger instance."""
        return logging.getLogger("ImageGenerationFlowTool")
    
    def _run(
        self,
        product_id: str,
        reference_url: str,
        product_name: str,
        product_features: list,
        style_requirements: Optional[dict] = None,
        approval_threshold: float = 0.85
    ) -> Dict[str, Any]:
        """
        Execute the image generation flow.
        
        Args:
            product_id: UUID string of the product
            reference_url: URL or path to reference image
            product_name: Name of the product
            product_features: List of product features
            style_requirements: Optional style requirements
            approval_threshold: Quality threshold (0-1)
            
        Returns:
            Dictionary with:
                - success: Whether generation succeeded
                - image_url: Final image URL if successful
                - attempts: Number of attempts made
                - error: Error message if failed
        """
        try:
            # Convert product_id to UUID
            pid = UUID(product_id)
            
            # Create flow instance
            flow = ImageGenerationFlow()
            self._flow_instances[pid] = flow
            
            # Prepare product info
            product_info = {
                "name": product_name,
                "features": product_features,
                "style": style_requirements or {},
                "threshold": approval_threshold
            }
            
            # Execute flow synchronously (agents typically run in sync context)
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            
            try:
                result = loop.run_until_complete(
                    flow.generate_image_for_product(
                        product_id=pid,
                        reference_url=reference_url,
                        product_info=product_info
                    )
                )
                
                return result
                
            finally:
                loop.close()
                
        except ValueError as e:
            self.logger.error(f"Invalid product_id format: {e}")
            return {
                "success": False,
                "error": f"Invalid product_id format: {e}"
            }
        except Exception as e:
            self.logger.error(f"Flow execution error: {str(e)}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_status(self, product_id: str) -> Dict[str, Any]:
        """
        Get the status of an ongoing or completed generation.
        
        Args:
            product_id: UUID string of the product
            
        Returns:
            Dictionary with current status information
        """
        try:
            pid = UUID(product_id)
            
            if pid not in self._flow_instances:
                return {
                    "status": "not_found",
                    "message": f"No generation flow found for product {product_id}"
                }
            
            flow = self._flow_instances[pid]
            return flow.get_generation_status()
            
        except ValueError as e:
            return {
                "status": "error",
                "message": f"Invalid product_id format: {e}"
            }


class ImageGenerationFlowStatusTool(BaseTool):
    """Tool for checking the status of image generation flows."""
    
    name: str = "check_image_generation_status"
    description: str = """
    Check the status of an ongoing or completed image generation flow.
    
    Provides information about:
    - Current status (not_started, in_progress, completed, failed)
    - Number of attempts made
    - Approval status
    - Generated image URL (if completed)
    - Latest feedback received
    
    Input: product_id (UUID string)
    """
    
    flow_tool: ImageGenerationFlowTool = Field(description="Reference to the generation flow tool")
    
    def _run(self, product_id: str) -> Dict[str, Any]:
        """Check the status of a generation flow."""
        return self.flow_tool.get_status(product_id)


# Manager Agent Integration Example
class ManagerAgentFlowInput(BaseModel):
    """Input model for manager agent flow requests."""
    product_id: str = Field(description="UUID of the product")
    reference_url: str = Field(description="URL or path to reference image")
    product_name: str = Field(description="Name of the product")
    product_features: list = Field(description="List of key product features")
    style_requirements: Optional[dict] = Field(default=None, description="Style preferences")
    approval_threshold: float = Field(default=0.85, description="Quality threshold (0-1)")


def create_flow_tools() -> tuple[ImageGenerationFlowTool, ImageGenerationFlowStatusTool]:
    """
    Create and return the flow tools for agent use.
    
    Returns:
        Tuple of (generation_tool, status_tool)
    """
    generation_tool = ImageGenerationFlowTool()
    status_tool = ImageGenerationFlowStatusTool(flow_tool=generation_tool)
    
    return generation_tool, status_tool