"""Data models for Swallowtail."""

from .product import ProductIdea, SupplierInfo, ProductListing
from .checkpoint import HumanCheckpoint, CheckpointType, CheckpointStatus
from .research import (
    TrendData, TrendSource, CompetitionLevel, MarketMaturity,
    MarketAnalysis, SupplierOption, MarketOpportunity, OpportunityScore
)

__all__ = [
    "ProductIdea",
    "SupplierInfo", 
    "ProductListing",
    "HumanCheckpoint",
    "CheckpointType",
    "CheckpointStatus",
    # Research models
    "TrendData",
    "TrendSource",
    "CompetitionLevel",
    "MarketMaturity",
    "MarketAnalysis",
    "SupplierOption",
    "MarketOpportunity",
    "OpportunityScore",
]