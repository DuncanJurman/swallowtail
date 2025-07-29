"""Shared state management for agents."""

import json
from enum import Enum
from typing import Any, Dict, Optional

import redis
from pydantic import BaseModel, Field

from .config import get_settings


class StateKey(str, Enum):
    """Standard keys for shared state."""
    
    CURRENT_PRODUCT = "current_product"
    SUPPLIER_INFO = "supplier_info"
    CONTENT_ASSETS = "content_assets"
    MARKETING_PLAN = "marketing_plan"
    WORKFLOW_STATUS = "workflow_status"
    HUMAN_CHECKPOINTS = "human_checkpoints"


class WorkflowStatus(str, Enum):
    """Workflow status values."""
    
    IDLE = "idle"
    RESEARCHING = "researching"
    AWAITING_PRODUCT_APPROVAL = "awaiting_product_approval"
    SOURCING = "sourcing"
    AWAITING_SUPPLIER_APPROVAL = "awaiting_supplier_approval"
    CREATING_CONTENT = "creating_content"
    AWAITING_CONTENT_APPROVAL = "awaiting_content_approval"
    PREPARING_MARKETING = "preparing_marketing"
    AWAITING_MARKETING_APPROVAL = "awaiting_marketing_approval"
    LAUNCHING = "launching"
    LIVE = "live"
    ERROR = "error"


class SharedState:
    """Manages shared state between agents using Redis."""
    
    def __init__(self, redis_client: Optional[redis.Redis] = None):
        """Initialize shared state manager."""
        if redis_client:
            self.redis = redis_client
        else:
            settings = get_settings()
            self.redis = redis.from_url(settings.redis_url, decode_responses=True)
        self.namespace = "swallowtail:state:"
    
    def _make_key(self, key: str) -> str:
        """Create namespaced Redis key."""
        return f"{self.namespace}{key}"
    
    def get(self, key: str) -> Optional[Any]:
        """Get value from shared state."""
        raw_value = self.redis.get(self._make_key(key))
        if raw_value is None:
            return None
        try:
            return json.loads(raw_value)
        except json.JSONDecodeError:
            return raw_value
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """Set value in shared state."""
        if isinstance(value, BaseModel):
            value = value.model_dump()
        
        serialized = json.dumps(value) if not isinstance(value, str) else value
        
        if ttl:
            self.redis.setex(self._make_key(key), ttl, serialized)
        else:
            self.redis.set(self._make_key(key), serialized)
    
    def delete(self, key: str) -> None:
        """Delete value from shared state."""
        self.redis.delete(self._make_key(key))
    
    def update_workflow_status(self, status: WorkflowStatus) -> None:
        """Update the current workflow status."""
        self.set(StateKey.WORKFLOW_STATUS, status.value)
    
    def get_workflow_status(self) -> Optional[WorkflowStatus]:
        """Get the current workflow status."""
        status = self.get(StateKey.WORKFLOW_STATUS)
        return WorkflowStatus(status) if status else None
    
    def clear_all(self) -> None:
        """Clear all state (use with caution)."""
        pattern = f"{self.namespace}*"
        for key in self.redis.scan_iter(match=pattern):
            self.redis.delete(key)