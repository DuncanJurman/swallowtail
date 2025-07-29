"""Data models for Swallowtail."""

from .product import ProductIdea, SupplierInfo, ProductListing
from .checkpoint import HumanCheckpoint, CheckpointType, CheckpointStatus
from .research import (
    TrendData, TrendSource, CompetitionLevel, MarketMaturity,
    MarketAnalysis, SupplierOption, MarketOpportunity, OpportunityScore
)
from .instance import Instance, InstanceAgent, InstanceTask, InstanceMedia, InstanceType, InstanceTaskStatus, TaskPriority
from .instance_schemas import (
    InstanceCreate, InstanceResponse, TaskSubmission, InstanceTaskResponse, InstanceMediaResponse,
    TaskUpdateRequest, TaskExecutionStep, TaskListFilters
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
    # Instance models
    "Instance",
    "InstanceAgent",
    "InstanceTask",
    "InstanceMedia",
    "InstanceType",
    "InstanceTaskStatus",
    "TaskPriority",
    # Instance schemas
    "InstanceCreate",
    "InstanceResponse",
    "TaskSubmission",
    "InstanceTaskResponse",
    "InstanceMediaResponse",
    "TaskUpdateRequest",
    "TaskExecutionStep",
    "TaskListFilters",
]