"""Base crew class for Swallowtail using CrewAI's native patterns."""

import logging
from abc import ABC
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml
from crewai import Agent, Crew, Process, Task, LLM
from crewai.agents.agent_builder.base_agent import BaseAgent
from crewai.project import CrewBase, agent, before_kickoff, after_kickoff, crew, task

from ..core.config import get_settings
from ..core.state import SharedState


@CrewBase
class SwallowtailCrewBase:
    """Enhanced CrewBase with Swallowtail-specific features."""
    
    agents: List[BaseAgent]
    tasks: List[Task]
    
    # Default configuration paths (can be overridden in subclasses)
    agents_config: Union[str, Dict[str, Any], None] = None
    tasks_config: Union[str, Dict[str, Any], None] = None
    
    def __init__(self, shared_state: Optional[SharedState] = None):
        """Initialize with optional shared state."""
        super().__init__()
        self.shared_state = shared_state or SharedState()
        self.logger = logging.getLogger(self.__class__.__name__)
        self.settings = get_settings()
        
        # Load configurations if paths are provided
        if isinstance(self.agents_config, str):
            self.agents_config = self._load_yaml(self.agents_config)
        if isinstance(self.tasks_config, str):
            self.tasks_config = self._load_yaml(self.tasks_config)
    
    def _load_yaml(self, path: str) -> Dict[str, Any]:
        """Load YAML configuration file."""
        config_path = Path(path)
        if not config_path.is_absolute():
            # Try relative to project root
            project_root = Path(__file__).parent.parent.parent
            config_path = project_root / path
        
        if not config_path.exists():
            self.logger.warning(f"Configuration file not found: {config_path}")
            return {}
        
        with open(config_path, 'r') as f:
            return yaml.safe_load(f) or {}
    
    def create_agent(
        self,
        config_name: str,
        tools: Optional[List[Any]] = None,
        **kwargs
    ) -> Agent:
        """Create an agent from configuration with optional overrides."""
        if not self.agents_config or config_name not in self.agents_config:
            raise ValueError(f"Agent configuration '{config_name}' not found")
        
        config = self.agents_config[config_name].copy()
        
        # Apply any overrides
        if tools is not None:
            config['tools'] = tools
        config.update(kwargs)
        
        # Set defaults from settings
        if 'llm' not in config:
            config['llm'] = LLM(
                model=self.settings.openai_model,
                temperature=config.get('temperature', 0.7)
            )
        
        if 'verbose' not in config:
            config['verbose'] = self.settings.debug
        
        return Agent(**config)
    
    def create_task(
        self,
        config_name: str,
        agent: Agent,
        **kwargs
    ) -> Task:
        """Create a task from configuration with optional overrides."""
        if not self.tasks_config or config_name not in self.tasks_config:
            raise ValueError(f"Task configuration '{config_name}' not found")
        
        config = self.tasks_config[config_name].copy()
        config['agent'] = agent
        
        # Apply any overrides
        config.update(kwargs)
        
        return Task(**config)
    
    @before_kickoff
    def prepare_crew(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        """Hook called before crew execution starts."""
        self.logger.info(f"Starting crew execution with inputs: {list(inputs.keys())}")
        
        # Store crew start time in shared state
        crew_id = inputs.get('crew_id', 'default')
        self.shared_state.set(f"crew:{crew_id}:start_time", inputs.get('start_time'))
        
        return inputs
    
    @after_kickoff
    def finalize_crew(self, output: Any) -> Any:
        """Hook called after crew execution completes."""
        self.logger.info("Crew execution completed")
        
        # Update shared state with completion
        crew_id = getattr(self, '_current_crew_id', 'default')
        self.shared_state.set(f"crew:{crew_id}:completed", True)
        
        return output
    
    def log_step(self, message: str, level: str = "info") -> None:
        """Log a step in crew execution."""
        if level == "error":
            self.logger.error(message)
        elif level == "warning":
            self.logger.warning(message)
        else:
            self.logger.info(message)
    
    def update_task_status(self, task_id: str, status: str, **kwargs) -> None:
        """Update task status in shared state."""
        status_data = {
            "status": status,
            "timestamp": kwargs.get('timestamp'),
            **kwargs
        }
        self.shared_state.set(f"task:{task_id}:status", status_data)
    
    @crew
    def crew(self) -> Crew:
        """Default crew configuration - should be overridden in subclasses."""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=self.settings.debug,
            memory=True,
            cache=True,
            max_rpm=self.settings.max_rpm if hasattr(self.settings, 'max_rpm') else None,
        )