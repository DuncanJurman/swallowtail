"""Product Orchestrator that uses CrewAI's native orchestration capabilities."""

import logging
from typing import Any, Dict, Optional
from uuid import UUID

from ..agents.base import AgentResult
from ..crews.product_task_crew import ProductTaskCrew


class ProductOrchestrator:
    """
    Product Orchestrator that creates and manages CrewAI crews for task execution.
    
    This is a lightweight wrapper that delegates all orchestration logic to CrewAI's
    native hierarchical process and planning capabilities.
    """
    
    def __init__(self):
        """Initialize the orchestrator."""
        self.logger = logging.getLogger("ProductOrchestrator")
    
    async def execute_task(
        self,
        task_id: UUID,
        task_description: str,
        product_id: UUID,
        context: Optional[Dict[str, Any]] = None
    ) -> AgentResult:
        """
        Execute a product task using CrewAI's hierarchical crew.
        
        Args:
            task_id: Unique identifier for the task
            task_description: Natural language description of the task
            product_id: ID of the product this task relates to
            context: Optional additional context for task execution
            
        Returns:
            AgentResult with execution results or error
        """
        try:
            self.logger.info(f"Creating crew for task {task_id}: {task_description}")
            
            # Create a crew specifically for this task
            task_crew = ProductTaskCrew(
                task_id=task_id,
                task_description=task_description,
                product_id=product_id
            )
            
            # Execute the crew asynchronously
            result = await task_crew.execute_async()
            
            if result["success"]:
                return AgentResult(
                    success=True,
                    data={
                        "task_id": str(task_id),
                        "result": result["result"],
                        "crew_type": "hierarchical",
                        "used_planning": True
                    },
                    metadata={
                        "execution_method": "crew_ai_hierarchical",
                        "product_id": str(product_id)
                    }
                )
            else:
                return AgentResult(
                    success=False,
                    error=result.get("error", "Unknown error occurred"),
                    data={"task_id": str(task_id)},
                    metadata={"product_id": str(product_id)}
                )
                
        except Exception as e:
            self.logger.error(f"Failed to execute task {task_id}: {str(e)}", exc_info=True)
            return AgentResult(
                success=False,
                error=str(e),
                data={"task_id": str(task_id)},
                metadata={"product_id": str(product_id)}
            )
    
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """
        Execute method for compatibility with BaseAgent interface.
        
        This extracts the required parameters from context and delegates to execute_task.
        """
        task_id = context.get('task_id')
        task_description = context.get('task_description')
        product_id = context.get('product_id')
        
        if not all([task_id, task_description, product_id]):
            return AgentResult(
                success=False,
                error="Missing required context: task_id, task_description, or product_id"
            )
        
        return await self.execute_task(
            task_id=UUID(task_id) if isinstance(task_id, str) else task_id,
            task_description=task_description,
            product_id=UUID(product_id) if isinstance(product_id, str) else product_id,
            context=context
        )