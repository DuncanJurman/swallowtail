"""Base agent class and utilities."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from crewai import Agent, Task
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field

from ..core.config import get_settings
from ..core.state import SharedState


class AgentResult(BaseModel):
    """Standard result format for agent outputs."""
    
    success: bool
    data: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class BaseAgent(ABC):
    """Base class for all Swallowtail agents."""
    
    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        tools: Optional[List[Any]] = None,
        shared_state: Optional[SharedState] = None,
    ):
        """Initialize base agent."""
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools or []
        self.shared_state = shared_state or SharedState()
        self.logger = logging.getLogger(f"agent.{name}")
        
        settings = get_settings()
        self.llm = ChatOpenAI(
            model=settings.openai_model,
            api_key=settings.openai_api_key,
            temperature=0.7,
        )
        
        self.agent = Agent(
            role=self.role,
            goal=self.goal,
            backstory=self.backstory,
            tools=self.tools,
            llm=self.llm,
            verbose=settings.debug,
            allow_delegation=False,
        )
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Execute the agent's main task."""
        pass
    
    def create_task(self, description: str, expected_output: str) -> Task:
        """Create a CrewAI task for this agent."""
        return Task(
            description=description,
            expected_output=expected_output,
            agent=self.agent,
        )
    
    def log_info(self, message: str) -> None:
        """Log info message."""
        self.logger.info(f"[{self.name}] {message}")
    
    def log_error(self, message: str) -> None:
        """Log error message."""
        self.logger.error(f"[{self.name}] {message}")
    
    def get_from_state(self, key: str) -> Optional[Any]:
        """Get value from shared state."""
        return self.shared_state.get(key)
    
    def set_in_state(self, key: str, value: Any) -> None:
        """Set value in shared state."""
        self.shared_state.set(key, value)