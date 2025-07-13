"""Orchestrator agent that coordinates all other agents."""

import asyncio
import uuid
from typing import Any, Dict, List, Optional

from ..core.state import StateKey, WorkflowStatus
from ..models.checkpoint import CheckpointType, HumanCheckpoint
from ..models.product import ProductIdea
from .base import AgentResult, BaseAgent


class OrchestratorAgent(BaseAgent):
    """Central orchestrator that manages the entire workflow."""
    
    def __init__(self, shared_state=None):
        """Initialize the orchestrator."""
        super().__init__(
            name="orchestrator",
            role="E-commerce Business Manager",
            goal="Coordinate all agents to successfully launch and manage products",
            backstory="""You are an experienced e-commerce business manager who 
            understands how to coordinate different departments to launch successful 
            products. You excel at planning, delegation, and ensuring smooth workflows.""",
            shared_state=shared_state,
        )
        self.agent_registry: Dict[str, BaseAgent] = {}
    
    def register_agent(self, agent_type: str, agent: BaseAgent) -> None:
        """Register an agent for orchestration."""
        self.agent_registry[agent_type] = agent
        self.log_info(f"Registered agent: {agent_type}")
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Execute the main orchestration workflow."""
        try:
            workflow_type = context.get("workflow", "product_launch")
            
            if workflow_type == "product_launch":
                return await self._execute_product_launch_workflow(context)
            else:
                return AgentResult(
                    success=False,
                    error=f"Unknown workflow type: {workflow_type}"
                )
        except Exception as e:
            self.log_error(f"Orchestration failed: {str(e)}")
            self.shared_state.update_workflow_status(WorkflowStatus.ERROR)
            return AgentResult(success=False, error=str(e))
    
    async def _execute_product_launch_workflow(
        self, context: Dict[str, Any]
    ) -> AgentResult:
        """Execute the product launch workflow."""
        self.log_info("Starting product launch workflow")
        self.shared_state.update_workflow_status(WorkflowStatus.RESEARCHING)
        
        # Step 1: Market Research
        if "market_research" in self.agent_registry:
            research_result = await self._run_market_research()
            if not research_result.success:
                return research_result
            
            # Create checkpoint for product selection
            checkpoint = await self._create_checkpoint(
                CheckpointType.PRODUCT_SELECTION,
                "Select Product to Launch",
                "Review the product suggestions and select one to proceed with",
                research_result.data or {}
            )
            
            # Wait for human approval
            self.shared_state.update_workflow_status(
                WorkflowStatus.AWAITING_PRODUCT_APPROVAL
            )
            
            # In a real implementation, we'd wait for the checkpoint to be resolved
            # For now, we'll return the checkpoint info
            return AgentResult(
                success=True,
                data={
                    "status": "awaiting_approval",
                    "checkpoint_id": checkpoint.id,
                    "checkpoint_type": checkpoint.type,
                    "product_ideas": research_result.data.get("products", [])
                }
            )
        
        return AgentResult(
            success=False,
            error="Market research agent not registered"
        )
    
    async def _run_market_research(self) -> AgentResult:
        """Run market research phase."""
        agent = self.agent_registry.get("market_research")
        if not agent:
            return AgentResult(success=False, error="Market research agent not found")
        
        self.log_info("Running market research")
        return await agent.execute({})
    
    async def _create_checkpoint(
        self,
        checkpoint_type: CheckpointType,
        title: str,
        description: str,
        data: Dict[str, Any]
    ) -> HumanCheckpoint:
        """Create a human checkpoint."""
        checkpoint = HumanCheckpoint(
            id=str(uuid.uuid4()),
            type=checkpoint_type,
            title=title,
            description=description,
            data=data
        )
        
        # Store checkpoint in shared state
        checkpoints = self.shared_state.get(StateKey.HUMAN_CHECKPOINTS) or {}
        checkpoints[checkpoint.id] = checkpoint.model_dump()
        self.shared_state.set(StateKey.HUMAN_CHECKPOINTS, checkpoints)
        
        self.log_info(f"Created checkpoint: {checkpoint.id} ({checkpoint_type})")
        return checkpoint
    
    async def resume_after_checkpoint(
        self, checkpoint_id: str, approved: bool, data: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """Resume workflow after checkpoint resolution."""
        checkpoints = self.shared_state.get(StateKey.HUMAN_CHECKPOINTS) or {}
        checkpoint_data = checkpoints.get(checkpoint_id)
        
        if not checkpoint_data:
            return AgentResult(success=False, error="Checkpoint not found")
        
        checkpoint = HumanCheckpoint(**checkpoint_data)
        
        if not approved:
            self.log_info(f"Checkpoint {checkpoint_id} was rejected")
            self.shared_state.update_workflow_status(WorkflowStatus.IDLE)
            return AgentResult(success=True, data={"status": "workflow_cancelled"})
        
        # Continue based on checkpoint type
        if checkpoint.type == CheckpointType.PRODUCT_SELECTION:
            return await self._continue_after_product_selection(data or {})
        
        return AgentResult(success=False, error="Unknown checkpoint type")
    
    async def _continue_after_product_selection(
        self, data: Dict[str, Any]
    ) -> AgentResult:
        """Continue workflow after product selection."""
        selected_product = data.get("selected_product")
        if not selected_product:
            return AgentResult(success=False, error="No product selected")
        
        # Store selected product in shared state
        self.shared_state.set(StateKey.CURRENT_PRODUCT, selected_product)
        
        # Next step would be sourcing
        self.log_info(f"Product selected: {selected_product.get('name', 'Unknown')}")
        self.shared_state.update_workflow_status(WorkflowStatus.SOURCING)
        
        # Continue with sourcing agent...
        # This is where we'd call the sourcing agent
        
        return AgentResult(
            success=True,
            data={"status": "proceeding_to_sourcing", "product": selected_product}
        )