"""Task data models."""

from pydantic import BaseModel, Field, field_validator
from typing import Optional, List, Dict, Any
from datetime import datetime


class Task(BaseModel):
    """Model for a task."""
    id: str = Field(..., description="Task ID", min_length=1)
    name: str = Field(..., description="Task name", min_length=1)
    type: str = Field(..., description="Task type: auto, manual, etc.", min_length=1)
    files: Optional[List[str]] = Field(None, description="Files involved in this task")
    action: str = Field(..., description="Action description", min_length=1)
    verify: Optional[str] = Field(None, description="Verification steps")
    done: Optional[str] = Field(None, description="Done criteria")
    status: str = Field("pending", description="Task status: pending, in_progress, complete, failed")
    result: Optional[str] = Field(None, description="Task execution result")
    
    @field_validator('name', 'action')
    @classmethod
    def validate_not_empty(cls, v: str) -> str:
        """Validate string fields are not empty."""
        if not v or not v.strip():
            raise ValueError("Field cannot be empty")
        return v.strip()


class TaskPlan(BaseModel):
    """Model for a task plan."""
    phase_number: int = Field(..., description="Phase number", gt=0)
    tasks: List[Task] = Field(..., description="List of tasks")
    created_at: datetime = Field(default_factory=datetime.now, description="Plan creation time")
    
    @field_validator('phase_number')
    @classmethod
    def validate_phase_number(cls, v: int) -> int:
        """Validate phase number is positive."""
        if v <= 0:
            raise ValueError("Phase number must be positive")
        return v


class TaskExecute(BaseModel):
    """Model for executing a task."""
    project_id: str = Field(..., description="Project ID", min_length=1)
    phase_number: int = Field(..., description="Phase number", gt=0)
    task_id: Optional[str] = Field(None, description="Specific task ID to execute (if None, execute all)")
    
    @field_validator('phase_number')
    @classmethod
    def validate_phase_number(cls, v: int) -> int:
        """Validate phase number is positive."""
        if v <= 0:
            raise ValueError("Phase number must be positive")
        return v
    
    @field_validator('project_id')
    @classmethod
    def validate_project_id(cls, v: str) -> str:
        """Validate project ID is not empty."""
        if not v or not v.strip():
            raise ValueError("Project ID cannot be empty")
        return v.strip()


class TaskProgress(BaseModel):
    """Model for task progress."""
    project_id: str = Field(..., description="Project ID")
    phase_number: int = Field(..., description="Phase number")
    current_task: Optional[str] = Field(None, description="Current task ID")
    completed_tasks: int = Field(0, description="Number of completed tasks")
    total_tasks: int = Field(0, description="Total number of tasks")
    status: str = Field("idle", description="Execution status: idle, running, complete, error")
    logs: List[str] = Field(default_factory=list, description="Execution logs")
