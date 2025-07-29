"""State models for CrewAI flows."""

from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from uuid import UUID
from datetime import datetime


class ImageGenerationState(BaseModel):
    """State model for image generation flow."""
    
    # Core identifiers - with defaults for initialization
    product_id: Optional[UUID] = None
    reference_image_url: str = ""
    product_name: str = ""
    product_features: List[str] = Field(default_factory=list)
    style_requirements: Dict[str, str] = Field(default_factory=dict)
    
    # Generation tracking
    attempts: int = 0
    max_attempts: int = 3
    approval_threshold: float = 0.85
    
    # Results storage
    generated_images: List[Dict[str, str]] = Field(default_factory=list)
    feedback_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Final results
    final_image_url: Optional[str] = None
    final_image_path: Optional[str] = None
    approved: bool = False
    completed_at: Optional[datetime] = None
    
    # Error tracking
    errors: List[Dict[str, str]] = Field(default_factory=list)
    
    class Config:
        """Pydantic configuration."""
        arbitrary_types_allowed = True
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None
        }