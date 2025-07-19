"""API routes for image generation workflow."""

from typing import Optional, List
import logging
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from ...workflows.image_generation_workflow import ImageGenerationWorkflow
from ...flows.image_generation_flow import ImageGenerationFlow
from uuid import UUID


logger = logging.getLogger(__name__)
router = APIRouter(prefix="/images", tags=["image-generation"])


class ImageGenerationRequest(BaseModel):
    """Request model for image generation."""
    product_id: str = Field(..., description="Product identifier")
    reference_image_url: str = Field(..., description="URL of reference image")
    product_name: str = Field(..., description="Name of the product")
    product_features: List[str] = Field(default_factory=list, description="Key features to highlight")
    style_requirements: Optional[dict] = Field(None, description="Optional style requirements")
    approval_threshold: float = Field(0.85, ge=0.0, le=1.0, description="Score threshold for approval")
    max_attempts: int = Field(3, ge=1, le=5, description="Maximum generation attempts")


class DetailedScores(BaseModel):
    """Detailed evaluation scores."""
    visual_fidelity: Optional[int] = None
    prompt_accuracy: Optional[int] = None
    technical_quality: Optional[int] = None
    product_accuracy: Optional[int] = None


class ImageGenerationResponse(BaseModel):
    """Response model for image generation."""
    success: bool
    image_url: Optional[str] = None
    score: Optional[float] = None
    attempts: int
    prompt: Optional[str] = None
    error: Optional[str] = None
    detailed_scores: Optional[DetailedScores] = None


@router.post("/generate", response_model=ImageGenerationResponse)
async def generate_product_image(request: ImageGenerationRequest):
    """
    Generate a product image based on reference.
    
    This endpoint triggers the image generation workflow which:
    1. Generates an image using gpt-image-1 from the reference
    2. Evaluates the generated image using gpt-4.1 vision
    3. Regenerates with feedback if not approved
    4. Returns the final approved image or error
    """
    try:
        logger.info(f"Starting image generation for product: {request.product_id}")
        
        # Create workflow instance
        workflow = ImageGenerationWorkflow(max_attempts=request.max_attempts)
        
        # Execute workflow
        result = await workflow.generate_product_image(
            product_id=request.product_id,
            reference_image_url=request.reference_image_url,
            product_name=request.product_name,
            product_features=request.product_features,
            style_requirements=request.style_requirements,
            approval_threshold=request.approval_threshold
        )
        
        if result['success']:
            response = ImageGenerationResponse(
                success=True,
                image_url=result['image_url'],
                score=result['score'],
                attempts=result['attempts'],
                prompt=result['prompt']
            )
            
            # Add detailed scores if available
            if 'detailed_scores' in result:
                response.detailed_scores = DetailedScores(**result['detailed_scores'])
            
            return response
        else:
            return ImageGenerationResponse(
                success=False,
                attempts=result['attempts'],
                error=result.get('error', 'Image generation failed')
            )
            
    except Exception as e:
        logger.error(f"Image generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-async")
async def generate_product_image_async(
    request: ImageGenerationRequest,
    background_tasks: BackgroundTasks
):
    """
    Generate a product image asynchronously.
    
    Returns immediately with a task ID. The actual generation
    happens in the background.
    """
    # For now, return a placeholder
    # In production, this would queue the task and return a tracking ID
    return {
        "task_id": f"img-gen-{request.product_id}",
        "status": "queued",
        "message": "Image generation queued for processing"
    }


@router.get("/status/{task_id}")
async def get_generation_status(task_id: str):
    """
    Get the status of an async image generation task.
    
    In production, this would check the actual task status
    from a task queue or database.
    """
    # Placeholder implementation
    return {
        "task_id": task_id,
        "status": "processing",
        "progress": 50,
        "message": "Evaluating generated image quality"
    }


# Flow-based endpoints
class FlowImageGenerationRequest(BaseModel):
    """Request model for flow-based image generation."""
    product_id: str = Field(..., description="Product UUID")
    reference_image_url: str = Field(..., description="URL or path to reference image")
    product_name: str = Field(..., description="Name of the product")
    product_features: List[str] = Field(..., description="Key features to highlight")
    style_requirements: Optional[dict] = Field(default_factory=dict, description="Style requirements")
    approval_threshold: float = Field(0.85, ge=0.0, le=1.0, description="Quality threshold for approval")


class FlowImageGenerationResponse(BaseModel):
    """Response model for flow-based image generation."""
    success: bool
    image_url: Optional[str] = None
    attempts: int
    metadata: dict


@router.post("/generate-flow", response_model=FlowImageGenerationResponse)
async def generate_product_image_with_flow(request: FlowImageGenerationRequest):
    """
    Generate a product image using CrewAI Flow.
    
    This endpoint uses the new flow-based architecture which:
    1. Orchestrates image generation and evaluation crews
    2. Automatically handles feedback loops
    3. Manages state throughout the process
    4. Returns the final approved image or error details
    """
    try:
        logger.info(f"Starting flow-based image generation for product: {request.product_id}")
        
        # Validate product_id as UUID
        try:
            product_uuid = UUID(request.product_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid product_id format. Must be a valid UUID.")
        
        # Create flow instance
        flow = ImageGenerationFlow()
        
        # Prepare product info
        product_info = {
            "name": request.product_name,
            "features": request.product_features,
            "style": request.style_requirements,
            "threshold": request.approval_threshold
        }
        
        # Execute flow
        result = await flow.generate_image_for_product(
            product_id=product_uuid,
            reference_url=request.reference_image_url,
            product_info=product_info
        )
        
        return FlowImageGenerationResponse(
            success=result["success"],
            image_url=result.get("image_url"),
            attempts=result.get("attempts", 0),
            metadata=result.get("metadata", {})
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Flow-based image generation error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# Flow status endpoints
@router.get("/flow-status/{product_id}")
async def get_flow_generation_status(product_id: str):
    """
    Get the status of a flow-based image generation.
    
    Note: This requires the flow instance to be stored in a
    persistent way (e.g., Redis, database) for production use.
    """
    try:
        # Validate product_id
        try:
            UUID(product_id)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid product_id format")
        
        # In production, this would retrieve the flow instance
        # from persistent storage and check its status
        return {
            "product_id": product_id,
            "status": "not_implemented",
            "message": "Status tracking requires persistent flow storage"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Status check error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))