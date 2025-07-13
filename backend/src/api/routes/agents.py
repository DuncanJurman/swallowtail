"""Agent-related API endpoints."""

from typing import Any, Dict, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from ...agents.market_research import MarketResearchAgent
from ...agents.orchestrator import OrchestratorAgent
from ...core.state import SharedState

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


@router.get("/workflow/status")
async def get_workflow_status() -> Dict[str, Any]:
    """Get current workflow status."""
    status = shared_state.get_workflow_status()
    current_product = shared_state.get("current_product")
    
    return {
        "status": status.value if status else "idle",
        "current_product": current_product,
    }