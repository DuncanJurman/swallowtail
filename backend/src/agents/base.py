"""Enhanced base agent class with full CrewAI support."""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union

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
    """Enhanced base class for all Swallowtail agents with full CrewAI support."""
    
    def __init__(
        self,
        name: str,
        role: str,
        goal: str,
        backstory: str,
        tools: Optional[List[Any]] = None,
        shared_state: Optional[SharedState] = None,
        # New CrewAI-specific parameters
        allow_delegation: bool = False,
        max_iter: int = 20,
        max_rpm: Optional[int] = None,
        max_execution_time: Optional[int] = None,
        verbose: Optional[bool] = None,
        memory: bool = False,
        cache: bool = True,
        system_template: Optional[str] = None,
        prompt_template: Optional[str] = None,
        response_template: Optional[str] = None,
        function_calling_llm: Optional[Any] = None,
        max_retry_limit: int = 2,
        respect_context_window: bool = True,
        use_system_prompt: bool = True,
        # Advanced features
        reasoning: bool = False,
        max_reasoning_attempts: Optional[int] = None,
        knowledge_sources: Optional[List[Any]] = None,
        embedder: Optional[Dict[str, Any]] = None,
        inject_date: bool = False,
        date_format: str = "%Y-%m-%d",
        multimodal: bool = False,
        # Custom parameters
        llm_config: Optional[Dict[str, Any]] = None,
        agent_config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize enhanced base agent with full CrewAI capabilities."""
        self.name = name
        self.role = role
        self.goal = goal
        self.backstory = backstory
        self.tools = tools or []
        self.shared_state = shared_state or SharedState()
        self.logger = logging.getLogger(f"agent.{name}")
        
        settings = get_settings()
        
        # Configure LLM with custom settings
        llm_params = {
            "model": settings.openai_model,
            "api_key": settings.openai_api_key,
            "temperature": 0.7,
        }
        if llm_config:
            llm_params.update(llm_config)
        
        self.llm = ChatOpenAI(**llm_params)
        
        # Determine verbose setting
        if verbose is None:
            verbose = settings.debug
        
        # Build agent configuration
        agent_params = {
            "role": self.role,
            "goal": self.goal,
            "backstory": self.backstory,
            "tools": self.tools,
            "llm": self.llm,
            "verbose": verbose,
            "allow_delegation": allow_delegation,
            "max_iter": max_iter,
            "max_rpm": max_rpm,
            "max_execution_time": max_execution_time,
            "memory": memory,
            "cache": cache,
            "max_retry_limit": max_retry_limit,
            "respect_context_window": respect_context_window,
            "use_system_prompt": use_system_prompt,
        }
        
        # Add optional parameters if provided
        if system_template:
            agent_params["system_template"] = system_template
        if prompt_template:
            agent_params["prompt_template"] = prompt_template
        if response_template:
            agent_params["response_template"] = response_template
        if function_calling_llm:
            agent_params["function_calling_llm"] = function_calling_llm
        
        # Advanced features
        agent_params["reasoning"] = reasoning
        if max_reasoning_attempts is not None:
            agent_params["max_reasoning_attempts"] = max_reasoning_attempts
        if knowledge_sources:
            agent_params["knowledge_sources"] = knowledge_sources
        if embedder:
            agent_params["embedder"] = embedder
        
        agent_params["inject_date"] = inject_date
        agent_params["date_format"] = date_format
        agent_params["multimodal"] = multimodal
        
        # Allow additional custom configuration
        if agent_config:
            agent_params.update(agent_config)
        
        self.agent = Agent(**agent_params)
    
    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> AgentResult:
        """Execute the agent's main task."""
        pass
    
    def create_task(
        self, 
        description: str, 
        expected_output: str,
        # Additional task parameters
        tools: Optional[List[Any]] = None,
        async_execution: bool = False,
        context: Optional[List[Task]] = None,
        output_json: Optional[type] = None,
        output_pydantic: Optional[type] = None,
        guardrail: Optional[Any] = None,
        human_input: bool = False,
    ) -> Task:
        """Create an enhanced CrewAI task with all available options."""
        task_params = {
            "description": description,
            "expected_output": expected_output,
            "agent": self.agent,
        }
        
        # Add optional parameters
        if tools:
            task_params["tools"] = tools
        if async_execution:
            task_params["async_execution"] = async_execution
        if context:
            task_params["context"] = context
        if output_json:
            task_params["output_json"] = output_json
        if output_pydantic:
            task_params["output_pydantic"] = output_pydantic
        if guardrail:
            task_params["guardrail"] = guardrail
        if human_input:
            task_params["human_input"] = human_input
        
        return Task(**task_params)
    
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
    
    @classmethod
    def from_config(
        cls,
        config: Dict[str, Any],
        name: str,
        shared_state: Optional[SharedState] = None,
        **kwargs
    ) -> "BaseAgent":
        """Create agent from configuration dictionary (e.g., from YAML)."""
        # Extract required fields
        role = config.get("role", "")
        goal = config.get("goal", "")
        backstory = config.get("backstory", "")
        
        # Merge config with any provided kwargs
        all_params = {
            "name": name,
            "role": role,
            "goal": goal,
            "backstory": backstory,
            "shared_state": shared_state,
        }
        all_params.update(config)
        all_params.update(kwargs)
        
        # Remove any None values
        all_params = {k: v for k, v in all_params.items() if v is not None}
        
        return cls(**all_params)