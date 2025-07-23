"""Human checkpoint API endpoints."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...core.state import SharedState, StateKey
from ...models.checkpoint import CheckpointStatus, HumanCheckpoint

router = APIRouter()

# Initialize shared state (TODO: Replace with instance-based system)
shared_state = SharedState()


class CheckpointResolution(BaseModel):
    """Request to resolve a checkpoint."""
    
    approved: bool
    notes: Optional[str] = None
    data: Optional[Dict[str, Any]] = None


class CheckpointResponse(BaseModel):
    """Checkpoint data response."""
    
    checkpoint: HumanCheckpoint
    related_data: Optional[Dict[str, Any]] = None


@router.get("/")
async def list_checkpoints() -> list[HumanCheckpoint]:
    """List all pending checkpoints."""
    checkpoints_data = shared_state.get(StateKey.HUMAN_CHECKPOINTS) or {}
    
    checkpoints = []
    for checkpoint_data in checkpoints_data.values():
        checkpoint = HumanCheckpoint(**checkpoint_data)
        if checkpoint.status == CheckpointStatus.PENDING:
            checkpoints.append(checkpoint)
    
    return checkpoints


@router.get("/{checkpoint_id}", response_model=CheckpointResponse)
async def get_checkpoint(checkpoint_id: str) -> CheckpointResponse:
    """Get a specific checkpoint."""
    checkpoints_data = shared_state.get(StateKey.HUMAN_CHECKPOINTS) or {}
    checkpoint_data = checkpoints_data.get(checkpoint_id)
    
    if not checkpoint_data:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    checkpoint = HumanCheckpoint(**checkpoint_data)
    
    # Get any related data based on checkpoint type
    related_data = None
    if checkpoint.type == "product_selection":
        related_data = checkpoint.data
    
    return CheckpointResponse(checkpoint=checkpoint, related_data=related_data)


@router.post("/{checkpoint_id}/resolve")
async def resolve_checkpoint(
    checkpoint_id: str,
    resolution: CheckpointResolution
) -> Dict[str, Any]:
    """Resolve a checkpoint and continue workflow."""
    checkpoints_data = shared_state.get(StateKey.HUMAN_CHECKPOINTS) or {}
    checkpoint_data = checkpoints_data.get(checkpoint_id)
    
    if not checkpoint_data:
        raise HTTPException(status_code=404, detail="Checkpoint not found")
    
    checkpoint = HumanCheckpoint(**checkpoint_data)
    
    # Update checkpoint status
    if resolution.approved:
        checkpoint.approve("user", resolution.notes)
    else:
        checkpoint.reject("user", resolution.notes)
    
    # Save updated checkpoint
    checkpoints_data[checkpoint_id] = checkpoint.model_dump()
    shared_state.set(StateKey.HUMAN_CHECKPOINTS, checkpoints_data)
    
    # TODO: Replace with instance-based task continuation
    return {
        "checkpoint_resolved": True,
        "message": "Legacy checkpoint system is deprecated. Please use instance-based task execution."
    }