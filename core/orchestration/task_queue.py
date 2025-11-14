"""
Task Queue Worker
Manages background task execution using queues.
"""

from typing import Callable, Dict, Any, Optional
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class TaskStatus(Enum):
    """Task execution status."""

    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    RETRY = "retry"


class Task:
    """Represents a background task."""

    def __init__(
        self,
        task_id: str,
        func: Callable,
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
        max_retries: int = 3,
    ):
        """
        Initialize a task.

        Args:
            task_id: Unique task identifier
            func: Function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            max_retries: Maximum number of retry attempts
        """
        self.task_id = task_id
        self.func = func
        self.args = args
        self.kwargs = kwargs or {}
        self.max_retries = max_retries

        self.status = TaskStatus.PENDING
        self.retries = 0
        self.result = None
        self.error = None
        self.created_at = datetime.utcnow()
        self.started_at: Optional[datetime] = None
        self.completed_at: Optional[datetime] = None

    def execute(self):
        """Execute the task."""
        self.status = TaskStatus.RUNNING
        self.started_at = datetime.utcnow()

        try:
            logger.info(f"Executing task: {self.task_id}")
            self.result = self.func(*self.args, **self.kwargs)
            self.status = TaskStatus.SUCCESS
            self.completed_at = datetime.utcnow()
            logger.info(f"Task completed successfully: {self.task_id}")

        except Exception as e:
            self.error = str(e)
            self.retries += 1

            if self.retries < self.max_retries:
                self.status = TaskStatus.RETRY
                logger.warning(
                    f"Task failed, will retry ({self.retries}/{self.max_retries}): {self.task_id}"
                )
            else:
                self.status = TaskStatus.FAILED
                self.completed_at = datetime.utcnow()
                logger.error(
                    f"Task failed after {self.retries} retries: {self.task_id} - {str(e)}"
                )

    def to_dict(self) -> Dict[str, Any]:
        """Convert task to dictionary."""
        return {
            "task_id": self.task_id,
            "status": self.status.value,
            "retries": self.retries,
            "max_retries": self.max_retries,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat()
            if self.completed_at
            else None,
            "error": self.error,
        }


class TaskQueue:
    """Simple in-memory task queue."""

    def __init__(self):
        """Initialize the task queue."""
        self.tasks: Dict[str, Task] = {}
        self.pending_queue: List[str] = []

    def add_task(
        self,
        task_id: str,
        func: Callable,
        args: tuple = (),
        kwargs: Dict[str, Any] = None,
        max_retries: int = 3,
    ) -> Task:
        """
        Add a task to the queue.

        Args:
            task_id: Unique task identifier
            func: Function to execute
            args: Positional arguments
            kwargs: Keyword arguments
            max_retries: Maximum retry attempts

        Returns:
            Task instance
        """
        task = Task(task_id, func, args, kwargs, max_retries)
        self.tasks[task_id] = task
        self.pending_queue.append(task_id)
        logger.info(f"Task added to queue: {task_id}")
        return task

    def process_tasks(self):
        """Process all pending tasks."""
        while self.pending_queue:
            task_id = self.pending_queue.pop(0)
            task = self.tasks.get(task_id)

            if task:
                task.execute()

                # Re-queue if retry needed
                if task.status == TaskStatus.RETRY:
                    self.pending_queue.append(task_id)

    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task."""
        task = self.tasks.get(task_id)
        return task.to_dict() if task else None

    def get_all_tasks(self) -> List[Dict[str, Any]]:
        """Get status of all tasks."""
        return [task.to_dict() for task in self.tasks.values()]


# Global task queue instance
task_queue = TaskQueue()
