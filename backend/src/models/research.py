"""Research Workshop data models."""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class TrendSource(str, Enum):
    """Sources for trend data."""
    GOOGLE_TRENDS = "google_trends"
    SOCIAL_MEDIA = "social_media"
    MARKETPLACE = "marketplace"
    NEWS = "news"
    COMPETITOR = "competitor"


class CompetitionLevel(str, Enum):
    """Competition intensity levels."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    SATURATED = "saturated"


class MarketMaturity(str, Enum):
    """Market lifecycle stage."""
    EMERGING = "emerging"
    GROWING = "growing"
    MATURE = "mature"
    DECLINING = "declining"


class TrendData(BaseModel):
    """Trend information from various sources."""
    source: TrendSource
    keywords: List[str]
    growth_rate: float = Field(..., ge=-1.0, le=10.0, description="Growth rate as decimal (0.35 = 35%)")
    current_volume: int = Field(..., ge=0, description="Current search/mention volume")
    three_month_avg: int = Field(..., ge=0, description="3-month average volume")
    yoy_change: float = Field(..., description="Year-over-year change rate")
    geographic_hotspots: List[str] = Field(default_factory=list, description="Top geographic regions")
    related_topics: List[str] = Field(default_factory=list)
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Data confidence 0-1")
    captured_at: datetime = Field(default_factory=datetime.utcnow)
    raw_data: Optional[Dict[str, Any]] = None


class MarketAnalysis(BaseModel):
    """Deep market analysis for an opportunity."""
    market_size_estimate: float = Field(..., ge=0, description="Estimated market size in USD")
    competition_level: CompetitionLevel
    average_price_range: tuple[float, float] = Field(..., description="(min_price, max_price)")
    top_competitors: List[Dict[str, Any]] = Field(default_factory=list)
    customer_pain_points: List[str] = Field(default_factory=list)
    seasonality_factor: float = Field(..., ge=0.0, le=1.0, description="0=no seasonality, 1=highly seasonal")
    market_maturity: MarketMaturity
    barrier_to_entry: str = Field(..., description="low, medium, high")
    regulatory_concerns: List[str] = Field(default_factory=list)
    market_trends: List[str] = Field(default_factory=list)


class SupplierOption(BaseModel):
    """Supplier information and pricing."""
    supplier_id: str
    name: str
    location: str
    unit_price: float = Field(..., ge=0)
    moq: int = Field(..., ge=1, description="Minimum order quantity")
    lead_time_days: int = Field(..., ge=1)
    shipping_cost_per_unit: float = Field(..., ge=0)
    rating: float = Field(..., ge=0.0, le=5.0)
    review_count: int = Field(default=0, ge=0)
    certifications: List[str] = Field(default_factory=list)
    payment_terms: str
    samples_available: bool = False
    customization_available: bool = False
    estimated_landed_cost: Optional[float] = None


class MarketOpportunity(BaseModel):
    """Complete market opportunity with all analysis."""
    id: Optional[str] = None
    title: str
    description: str
    trend_data: TrendData
    market_analysis: Optional[MarketAnalysis] = None
    sourcing_options: Optional[List[SupplierOption]] = None
    score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Overall opportunity score")
    profit_margin_estimate: Optional[float] = None
    risk_assessment: Optional[Dict[str, Any]] = None
    recommended_action: Optional[str] = None
    discovery_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = "pending"
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class OpportunityScore(BaseModel):
    """Detailed scoring breakdown for an opportunity."""
    overall_score: float = Field(..., ge=0.0, le=1.0)
    market_demand_score: float = Field(..., ge=0.0, le=1.0)
    competition_score: float = Field(..., ge=0.0, le=1.0)
    profitability_score: float = Field(..., ge=0.0, le=1.0)
    sourcing_ease_score: float = Field(..., ge=0.0, le=1.0)
    trend_momentum_score: float = Field(..., ge=0.0, le=1.0)
    risk_score: float = Field(..., ge=0.0, le=1.0)
    scoring_factors: Dict[str, float] = Field(default_factory=dict)
    explanation: str