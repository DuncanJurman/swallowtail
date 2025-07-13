"""Human checkpoint models."""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


class CheckpointType(str, Enum):
    """Types of human checkpoints."""
    
    PRODUCT_SELECTION = "product_selection"
    SUPPLIER_APPROVAL = "supplier_approval"
    CONTENT_REVIEW = "content_review"
    MARKETING_APPROVAL = "marketing_approval"
    CUSTOM = "custom"


class CheckpointStatus(str, Enum):
    """Status of a checkpoint."""
    
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUESTED = "revision_requested"


class HumanCheckpoint(BaseModel):
    """Represents a point where human approval is needed."""
    
    id: str
    type: CheckpointType
    title: str
    description: str
    data: Dict[str, Any]
    status: CheckpointStatus = CheckpointStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None
    resolved_by: Optional[str] = None
    resolution_notes: Optional[str] = None
    
    def approve(self, user_id: str, notes: Optional[str] = None) -> None:
        """Approve the checkpoint."""
        self.status = CheckpointStatus.APPROVED
        self.resolved_at = datetime.utcnow()
        self.resolved_by = user_id
        self.resolution_notes = notes
    
    def reject(self, user_id: str, notes: Optional[str] = None) -> None:
        """Reject the checkpoint."""
        self.status = CheckpointStatus.REJECTED
        self.resolved_at = datetime.utcnow()
        self.resolved_by = user_id
        self.resolution_notes = notes
    
    def request_revision(self, user_id: str, notes: str) -> None:
        """Request revision for the checkpoint."""
        self.status = CheckpointStatus.REVISION_REQUESTED
        self.resolved_at = datetime.utcnow()
        self.resolved_by = user_id
        self.resolution_notes = notes