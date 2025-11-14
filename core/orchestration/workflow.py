"""
Workflow orchestration for complex multi-step processes.
"""

from typing import List, Dict, Any, Callable, Optional
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class StepStatus(Enum):
    """Workflow step status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    SKIPPED = "skipped"


class WorkflowStep:
    """Represents a single step in a workflow."""

    def __init__(
        self,
        step_id: str,
        name: str,
        func: Callable,
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
        depends_on: List[str] = None,
    ):
        """
        Initialize a workflow step.

        Args:
            step_id: Unique step identifier
            name: Human-readable step name
            func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            depends_on: List of step IDs this step depends on
        """
        self.step_id = step_id
        self.name = name
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.depends_on = depends_on or []

        self.status = StepStatus.PENDING
        self.result = None
        self.error = None
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def execute(self, context: Dict[str, Any] = None) -> Any:
        """
        Execute the step.

        Args:
            context: Shared context from previous steps

        Returns:
            Step result
        """
        self.status = StepStatus.RUNNING
        self.started_at = datetime.utcnow()

        try:
            logger.info(f"Executing step: {self.name} ({self.step_id})")

            # Merge context into kwargs if provided
            if context:
                self.kwargs.update({"context": context})

            self.result = self.func(*self.args, **self.kwargs)
            self.status = StepStatus.SUCCESS
            self.completed_at = datetime.utcnow()

            logger.info(f"Step completed: {self.name}")
            return self.result

        except Exception as e:
            self.error = str(e)
            self.status = StepStatus.FAILED
            self.completed_at = datetime.utcnow()
            logger.error(f"Step failed: {self.name} - {str(e)}")
            raise


class Workflow:
    """Manages multi-step workflows with dependencies."""

    def __init__(self, workflow_id: str, name: str):
        """
        Initialize a workflow.

        Args:
            workflow_id: Unique workflow identifier
            name: Human-readable workflow name
        """
        self.workflow_id = workflow_id
        self.name = name
        self.steps: Dict[str, WorkflowStep] = {}
        self.execution_order: List[str] = []
        self.context: Dict[str, Any] = {}

        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None
        self.success = False

    def add_step(
        self,
        step_id: str,
        name: str,
        func: Callable,
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
        depends_on: List[str] = None,
    ):
        """Add a step to the workflow."""
        step = WorkflowStep(step_id, name, func, args, kwargs, depends_on)
        self.steps[step_id] = step
        logger.info(f"Added step to workflow '{self.name}': {name}")

    def _resolve_execution_order(self):
        """Resolve step execution order based on dependencies."""
        visited = set()
        order = []

        def visit(step_id: str):
            if step_id in visited:
                return

            step = self.steps[step_id]
            for dep in step.depends_on:
                if dep in self.steps:
                    visit(dep)

            visited.add(step_id)
            order.append(step_id)

        for step_id in self.steps:
            visit(step_id)

        self.execution_order = order

    def execute(self, initial_context: Dict[str, Any] = None) -> bool:
        """
        Execute the workflow.

        Args:
            initial_context: Initial context data

        Returns:
            bool: True if workflow completed successfully
        """
        self.started_at = datetime.utcnow()
        self.context = initial_context or {}

        logger.info(f"Starting workflow: {self.name}")

        # Resolve execution order
        self._resolve_execution_order()

        try:
            for step_id in self.execution_order:
                step = self.steps[step_id]

                # Check if dependencies succeeded
                dependencies_met = all(
                    self.steps[dep_id].status == StepStatus.SUCCESS
                    for dep_id in step.depends_on
                    if dep_id in self.steps
                )

                if not dependencies_met:
                    step.status = StepStatus.SKIPPED
                    logger.warning(f"Skipping step (dependencies not met): {step.name}")
                    continue

                # Execute step
                result = step.execute(self.context)

                # Store result in context for next steps
                self.context[step_id] = result

            # Check if all steps succeeded
            self.success = all(
                step.status in [StepStatus.SUCCESS, StepStatus.SKIPPED]
                for step in self.steps.values()
            )

            self.completed_at = datetime.utcnow()

            if self.success:
                logger.info(f"Workflow completed successfully: {self.name}")
            else:
                logger.error(f"Workflow failed: {self.name}")

            return self.success

        except Exception as e:
            self.completed_at = datetime.utcnow()
            logger.error(f"Workflow failed with error: {self.name} - {str(e)}")
            return False

    def get_status(self) -> Dict[str, Any]:
        """Get workflow status."""
        return {
            "workflow_id": self.workflow_id,
            "name": self.name,
            "success": self.success,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "steps": {
                step_id: {
                    "name": step.name,
                    "status": step.status.value,
                    "error": step.error,
                }
                for step_id, step in self.steps.items()
            },
        }
