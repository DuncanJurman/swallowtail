"""Pydantic models for image evaluation structured outputs."""

from pydantic import BaseModel, Field
from typing import List, Literal


class ImageEvaluationOutput(BaseModel):
    """Structured output for image evaluation tasks."""
    
    # Individual category scores (0-100)
    overall_score: int = Field(
        description="Overall quality score from 0-100",
        ge=0,
        le=100
    )
    visual_fidelity_score: int = Field(
        description="How well the generated image matches the reference style, color, and mood (0-100)",
        ge=0,
        le=100
    )
    product_accuracy_score: int = Field(
        description="How accurately product features are represented (0-100)",
        ge=0,
        le=100
    )
    technical_quality_score: int = Field(
        description="Image sharpness, lighting, and composition quality (0-100)",
        ge=0,
        le=100
    )
    professional_appearance_score: int = Field(
        description="Overall professional look and polish (0-100)",
        ge=0,
        le=100
    )
    ecommerce_suitability_score: int = Field(
        description="How suitable the image is for e-commerce use (0-100)",
        ge=0,
        le=100
    )
    
    # Approval decision
    approved: bool = Field(
        description="Whether the image meets the approval threshold"
    )
    
    # Feedback and improvements
    feedback: List[str] = Field(
        default_factory=list,
        description="List of specific, actionable improvement suggestions if not approved"
    )
    
    # Confidence level
    confidence: Literal["High", "Medium", "Low"] = Field(
        description="Confidence level in the evaluation"
    )
    
    # Optional detailed analysis
    strengths: List[str] = Field(
        default_factory=list,
        description="Key strengths of the generated image"
    )
    weaknesses: List[str] = Field(
        default_factory=list,
        description="Key weaknesses or areas for improvement"
    )
    
    class Config:
        """Pydantic config."""
        json_schema_extra = {
            "example": {
                "overall_score": 88,
                "visual_fidelity_score": 92,
                "product_accuracy_score": 85,
                "technical_quality_score": 90,
                "professional_appearance_score": 88,
                "ecommerce_suitability_score": 86,
                "approved": True,
                "feedback": [],
                "confidence": "High",
                "strengths": [
                    "Excellent color matching with reference",
                    "Product features clearly visible",
                    "Professional lighting"
                ],
                "weaknesses": [
                    "Slight shadow inconsistency on left side"
                ]
            }
        }