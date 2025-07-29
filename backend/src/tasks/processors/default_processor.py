"""Default task processor for general tasks."""

import logging
import time
from typing import Dict, Any
from datetime import datetime, timezone

from src.tasks.base_processor import BaseTaskProcessor
from src.models.instance_schemas import TaskExecutionStep

logger = logging.getLogger(__name__)


class DefaultTaskProcessor(BaseTaskProcessor):
    """Default processor for tasks without specific handlers."""
    
    def process(self) -> Dict[str, Any]:
        """Process a general task."""
        logger.info(f"Processing task {self.task_id} with default processor")
        
        # Step 1: Parse intent
        self.update_progress(10, "Parsing task intent")
        
        step1 = TaskExecutionStep(
            step_id="parse_intent",
            agent="DefaultProcessor",
            action="Parsing task description",
            status="in_progress",
            started_at=datetime.now(timezone.utc)
        )
        self.add_execution_step(step1)
        
        intent = self.parse_intent()
        self.task.parsed_intent = intent
        
        step1.status = "completed"
        step1.completed_at = datetime.now(timezone.utc)
        step1.output = {"intent": intent}
        self.add_execution_step(step1)
        
        # Step 2: Simulate processing
        self.update_progress(50, "Processing task")
        
        step2 = TaskExecutionStep(
            step_id="process",
            agent="DefaultProcessor",
            action="Executing task logic",
            status="in_progress",
            started_at=datetime.now(timezone.utc)
        )
        self.add_execution_step(step2)
        
        # Simulate work
        time.sleep(2)
        
        result = {
            "message": f"Task processed: {self.task.description}",
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "processor": "DefaultTaskProcessor"
        }
        
        step2.status = "completed"
        step2.completed_at = datetime.now(timezone.utc)
        step2.output = result
        self.add_execution_step(step2)
        
        # Step 3: Set output
        self.update_progress(90, "Finalizing results")
        
        self.set_output(
            output_format="json",
            output_data=result
        )
        
        self.update_progress(100, "Task completed")
        
        return {
            "status": "success",
            "result": result
        }