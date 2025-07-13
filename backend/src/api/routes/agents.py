"""Agent-related API endpoints."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...agents.market_research import MarketResearchAgent
from ...agents.orchestrator import OrchestratorAgent
from ...core.state import SharedState, WorkflowStatus

router = APIRouter()


class WorkflowRequest(BaseModel):
    """Request to start a workflow."""
    
    workflow_type: str = "product_launch"
    context: Dict[str, Any] = {}


class WorkflowResponse(BaseModel):
    """Response from workflow execution."""
    
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


# Initialize agents (in production, this would be more sophisticated)
shared_state = SharedState()
orchestrator = OrchestratorAgent(shared_state)
market_research = MarketResearchAgent(shared_state)

# Register agents with orchestrator
orchestrator.register_agent("market_research", market_research)


@router.post("/workflow/start", response_model=WorkflowResponse)
async def start_workflow(request: WorkflowRequest) -> WorkflowResponse:
    """Start a new workflow."""
    try:
        # Check if a workflow is already running
        current_status = shared_state.get_workflow_status()
        if current_status and current_status.value not in ["idle", "error", "completed"]:
            return WorkflowResponse(
                success=False,
                error=f"Cannot start new workflow. Current workflow is in '{current_status.value}' state."
            )
        
        result = await orchestrator.execute({
            "workflow": request.workflow_type,
            **request.context
        })
        
        return WorkflowResponse(
            success=result.success,
            data=result.data,
            error=result.error
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/workflow/cancel", response_model=WorkflowResponse)
async def cancel_workflow() -> WorkflowResponse:
    """Cancel the current workflow."""
    try:
        current_status = shared_state.get_workflow_status()
        if not current_status or current_status.value in ["idle", "completed"]:
            return WorkflowResponse(
                success=False,
                error="No active workflow to cancel."
            )
        
        # Clear all workflow-related state
        shared_state.update_workflow_status(WorkflowStatus.IDLE)
        shared_state.delete("current_product")
        shared_state.delete("pending_checkpoint")
        shared_state.delete("product_ideas")
        shared_state.delete("selected_product")
        
        return WorkflowResponse(
            success=True,
            data={"message": f"Workflow in '{current_status.value}' state has been cancelled."}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/workflow/status")
async def get_workflow_status() -> Dict[str, Any]:
    """Get current workflow status."""
    status = shared_state.get_workflow_status()
    current_product = shared_state.get("current_product")
    
    return {
        "status": status.value if status else "idle",
        "current_product": current_product,
    }