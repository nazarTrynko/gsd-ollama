"""Project data models."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ProjectCreate(BaseModel):
    """Model for creating a new project."""
    name: str = Field(..., description="Project name")
    description: str = Field(..., description="Project description")
    initial_task: Optional[str] = Field(None, description="Initial task or goal")
    project_path: Optional[str] = Field(None, description="Custom project path")


class ProjectInfo(BaseModel):
    """Model for project information."""
    id: str = Field(..., description="Project ID (path)")
    name: str = Field(..., description="Project name")
    description: Optional[str] = Field(None, description="Project description")
    path: str = Field(..., description="Project path")
    exists: bool = Field(..., description="Whether project files exist")
    created_at: Optional[datetime] = Field(None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(None, description="Last update timestamp")


class ProjectList(BaseModel):
    """Model for project list response."""
    projects: List[ProjectInfo] = Field(..., description="List of projects")
    total: int = Field(..., description="Total number of projects")
