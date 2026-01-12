"""Task data models."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class Task(BaseModel):
    """Model for a task."""
    id: str = Field(..., description="Task ID")
    name: str = Field(..., description="Task name")
    type: str = Field(..., description="Task type: auto, manual, etc.")
    files: Optional[List[str]] = Field(None, description="Files involved in this task")
    action: str = Field(..., description="Action description")
    verify: Optional[str] = Field(None, description="Verification steps")
    done: Optional[str] = Field(None, description="Done criteria")
    status: str = Field("pending", description="Task status: pending, in_progress, complete, failed")
    result: Optional[str] = Field(None, description="Task execution result")


class TaskPlan(BaseModel):
    """Model for a task plan."""
    phase_number: int = Field(..., description="Phase number")
    tasks: List[Task] = Field(..., description="List of tasks")
    created_at: datetime = Field(default_factory=datetime.now, description="Plan creation time")


class TaskExecute(BaseModel):
    """Model for executing a task."""
    project_id: str = Field(..., description="Project ID")
    phase_number: int = Field(..., description="Phase number")
    task_id: Optional[str] = Field(None, description="Specific task ID to execute (if None, execute all)")


class TaskProgress(BaseModel):
    """Model for task progress."""
    project_id: str = Field(..., description="Project ID")
    phase_number: int = Field(..., description="Phase number")
    current_task: Optional[str] = Field(None, description="Current task ID")
    completed_tasks: int = Field(0, description="Number of completed tasks")
    total_tasks: int = Field(0, description="Total number of tasks")
    status: str = Field("idle", description="Execution status: idle, running, complete, error")
    logs: List[str] = Field(default_factory=list, description="Execution logs")
