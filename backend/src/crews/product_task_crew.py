"""Product Task Crew implementation using CrewAI's hierarchical process."""

import asyncio
import json
import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import UUID

from crewai import Agent, Crew, Process, Task
from crewai.project import agent, before_kickoff, after_kickoff, crew, task
from crewai_tools import SerperDevTool
from pydantic import BaseModel

from .base import SwallowtailCrewBase
from ..agents.image_generation import ImageGenerationAgent
from ..agents.image_evaluator import ImageEvaluatorAgent
from ..core.database import get_db
from ..models.database import ProductTask, TaskStatus


class SubtaskPlan(BaseModel):
    """Structure for subtask planning."""
    id: str
    type: str
    description: str
    agent: str
    priority: int
    dependencies: List[str] = []
    estimated_time: str = "unknown"


class ExecutionPlan(BaseModel):
    """Complete execution plan structure."""
    subtasks: List[SubtaskPlan]
    total_estimated_time: str
    complexity: str


class ProductTaskCrew(SwallowtailCrewBase):
    """Crew for handling product-specific tasks with intelligent orchestration."""
    
    agents_config = "src/config/agents.yaml"
    tasks_config = "src/config/tasks.yaml"
    
    def __init__(self, task_id: UUID, task_description: str, product_id: UUID):
        """Initialize with specific task details."""
        super().__init__()
        self.task_id = task_id
        self.task_description = task_description
        self.product_id = product_id
        self.logger = logging.getLogger(f"ProductTaskCrew[{task_id}]")
        
        # Initialize specialized agent instances
        self.image_gen_agent = ImageGenerationAgent()
        self.image_eval_agent = ImageEvaluatorAgent()
        
        # Tools for agents
        self.search_tool = SerperDevTool()
    
    @before_kickoff
    def prepare_task_execution(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Prepare for task execution."""
        self.logger.info(f"Starting execution for task: {self.task_description}")
        
        # Update task status in database
        asyncio.create_task(self._update_task_status(
            status=TaskStatus.IN_PROGRESS,
            assigned_agent="product_orchestrator"
        ))
        
        # Add task context to inputs
        inputs.update({
            "task_id": str(self.task_id),
            "product_id": str(self.product_id),
            "task_description": self.task_description,
            "crew_id": f"task_{self.task_id}",
            "start_time": datetime.now(timezone.utc).isoformat()
        })
        
        return inputs
    
    @after_kickoff
    def complete_task_execution(self, output: Any) -> Any:
        """Handle task completion."""
        self.logger.info("Task execution completed")
        
        # Parse output and update task status
        if hasattr(output, 'raw'):
            result_data = {"output": output.raw}
            if hasattr(output, 'pydantic') and output.pydantic:
                result_data["structured_output"] = output.pydantic.dict()
        else:
            result_data = {"output": str(output)}
        
        # Update task status
        asyncio.create_task(self._update_task_status(
            status=TaskStatus.COMPLETED,
            result_data=result_data
        ))
        
        return output
    
    @agent
    def orchestrator(self) -> Agent:
        """Product orchestrator agent that manages task execution."""
        return self.create_agent(
            "product_orchestrator",
            tools=[self.search_tool]
        )
    
    @agent
    def image_generator(self) -> Agent:
        """Image generation specialist."""
        return self.create_agent(
            "image_generator",
            tools=[]  # Uses internal OpenAI service
        )
    
    @agent
    def image_evaluator(self) -> Agent:
        """Image evaluation specialist."""
        return self.create_agent(
            "image_evaluator",
            tools=[]  # Uses internal evaluation logic
        )
    
    @agent
    def market_researcher(self) -> Agent:
        """Market research specialist (dummy for now)."""
        return self.create_agent(
            "market_researcher",
            tools=[self.search_tool]
        )
    
    @agent
    def content_writer(self) -> Agent:
        """Content writing specialist (dummy for now)."""
        return self.create_agent(
            "content_writer",
            tools=[]
        )
    
    @agent
    def pricing_analyst(self) -> Agent:
        """Pricing analysis specialist (dummy for now)."""
        return self.create_agent(
            "pricing_analyst",
            tools=[self.search_tool]
        )
    
    @agent
    def seo_specialist(self) -> Agent:
        """SEO optimization specialist (dummy for now)."""
        return self.create_agent(
            "seo_specialist",
            tools=[self.search_tool]
        )
    
    @task
    def interpret_task(self) -> Task:
        """Initial task to interpret user request and create execution plan."""
        return self.create_task(
            "interpret_user_task",
            agent=self.orchestrator(),
            output_pydantic=ExecutionPlan
        )
    
    def create_dynamic_tasks(self, execution_plan: ExecutionPlan) -> List[Task]:
        """Create tasks dynamically based on execution plan."""
        tasks = []
        agent_map = {
            "image_generator": self.image_generator(),
            "image_evaluator": self.image_evaluator(),
            "market_researcher": self.market_researcher(),
            "content_writer": self.content_writer(),
            "pricing_analyst": self.pricing_analyst(),
            "seo_specialist": self.seo_specialist(),
        }
        
        task_map = {}  # Track created tasks for dependencies
        
        for subtask in execution_plan.subtasks:
            # Get the appropriate agent
            agent = agent_map.get(subtask.agent)
            if not agent:
                self.logger.warning(f"Unknown agent type: {subtask.agent}")
                continue
            
            # Build context from dependencies
            context = []
            for dep_id in subtask.dependencies:
                if dep_id in task_map:
                    context.append(task_map[dep_id])
            
            # Create the task
            task = Task(
                description=subtask.description,
                expected_output=f"Completed {subtask.type} with detailed results",
                agent=agent,
                context=context if context else None
            )
            
            tasks.append(task)
            task_map[subtask.id] = task
        
        return tasks
    
    @crew
    def crew(self) -> Crew:
        """Create a hierarchical crew with dynamic task generation."""
        # First, we need to interpret the task
        interpretation_crew = Crew(
            agents=[self.orchestrator()],
            tasks=[self.interpret_task()],
            process=Process.sequential,
            verbose=True
        )
        
        # Execute interpretation to get the plan
        interpretation_result = interpretation_crew.kickoff(inputs={
            "task_description": self.task_description,
            "product_id": str(self.product_id)
        })
        
        # Extract execution plan
        if hasattr(interpretation_result, 'pydantic') and interpretation_result.pydantic:
            execution_plan = interpretation_result.pydantic
        else:
            # Fallback: create a simple plan
            self.logger.warning("Failed to get structured plan, using fallback")
            execution_plan = ExecutionPlan(
                subtasks=[
                    SubtaskPlan(
                        id="1",
                        type="general",
                        description=self.task_description,
                        agent="content_writer",
                        priority=1
                    )
                ],
                total_estimated_time="unknown",
                complexity="medium"
            )
        
        # Create dynamic tasks based on plan
        dynamic_tasks = self.create_dynamic_tasks(execution_plan)
        
        if not dynamic_tasks:
            # Fallback task
            dynamic_tasks = [
                Task(
                    description=f"Complete task: {self.task_description}",
                    expected_output="Task completed successfully",
                    agent=self.content_writer()
                )
            ]
        
        # Create execution crew
        all_agents = [
            self.orchestrator(),
            self.image_generator(),
            self.image_evaluator(),
            self.market_researcher(),
            self.content_writer(),
            self.pricing_analyst(),
            self.seo_specialist()
        ]
        
        return Crew(
            agents=all_agents,
            tasks=dynamic_tasks,
            process=Process.hierarchical,
            manager_llm=self.settings.openai_model,  # Manager uses same model
            verbose=True,
            memory=True,
            planning=True,  # Enable planning
            planning_llm=self.settings.openai_model,
        )
    
    async def _update_task_status(
        self,
        status: TaskStatus,
        assigned_agent: Optional[str] = None,
        result_data: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None
    ):
        """Update task status in database."""
        try:
            async for db in get_db():
                task = await db.get(ProductTask, self.task_id)
                if task:
                    task.status = status
                    
                    if assigned_agent:
                        task.assigned_agent = assigned_agent
                    
                    if status == TaskStatus.IN_PROGRESS and not task.started_at:
                        task.started_at = datetime.now(timezone.utc)
                    elif status in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                        task.completed_at = datetime.now(timezone.utc)
                    
                    if result_data:
                        task.result_data = result_data
                    
                    if error_message:
                        task.error_message = error_message
                    
                    await db.commit()
                    
                    # Notify about status change
                    self.shared_state.set(
                        f"task_status:{self.product_id}:{self.task_id}",
                        status.value
                    )
                break
                
        except Exception as e:
            self.logger.error(f"Failed to update task status: {str(e)}")
    
    async def execute_async(self) -> Dict[str, Any]:
        """Execute the crew asynchronously."""
        try:
            # Run crew execution in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(
                None,
                self.crew().kickoff,
                {
                    "task_description": self.task_description,
                    "product_id": str(self.product_id)
                }
            )
            
            return {
                "success": True,
                "result": result.raw if hasattr(result, 'raw') else str(result),
                "task_id": str(self.task_id)
            }
            
        except Exception as e:
            self.logger.error(f"Task execution failed: {str(e)}")
            await self._update_task_status(
                status=TaskStatus.FAILED,
                error_message=str(e)
            )
            return {
                "success": False,
                "error": str(e),
                "task_id": str(self.task_id)
            }