"""Product-related data models."""

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class ProductIdea(BaseModel):
    """Represents a product idea from market research."""
    
    name: str
    description: str
    category: str
    target_audience: str
    key_benefits: List[str]
    search_volume_trend: Optional[str] = None
    competition_level: Optional[str] = None
    estimated_demand: Optional[str] = None
    rationale: str
    data_sources: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)


class SupplierInfo(BaseModel):
    """Information about a product supplier."""
    
    supplier_name: str
    supplier_url: Optional[str] = None
    unit_cost: float
    minimum_order_quantity: int
    shipping_cost: float
    lead_time_days: int
    supplier_rating: Optional[float] = None
    payment_terms: Optional[str] = None
    notes: Optional[str] = None


class ProductListing(BaseModel):
    """Complete product listing information."""
    
    # Basic info
    title: str
    description: str
    features: List[str]
    specifications: dict[str, str] = Field(default_factory=dict)
    
    # Pricing
    cost: float
    retail_price: float
    sale_price: Optional[float] = None
    
    # Content
    images: List[str] = Field(default_factory=list)
    videos: List[str] = Field(default_factory=list)
    
    # SEO
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    
    # Status
    status: str = "draft"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)