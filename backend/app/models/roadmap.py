"""Roadmap data models."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


class Phase(BaseModel):
    """Model for a roadmap phase."""
    number: int = Field(..., description="Phase number")
    name: str = Field(..., description="Phase name")
    description: str = Field(..., description="Phase description")
    status: str = Field("pending", description="Phase status: pending, in_progress, complete")
    tasks: Optional[List[str]] = Field(None, description="List of tasks in this phase")


class Milestone(BaseModel):
    """Model for a milestone."""
    name: str = Field(..., description="Milestone name")
    phases: List[Phase] = Field(..., description="Phases in this milestone")
    status: str = Field("pending", description="Milestone status")


class RoadmapCreate(BaseModel):
    """Model for creating a roadmap."""
    project_id: Optional[str] = Field(None, description="Project ID (optional, can be inferred from URL)")
    description: Optional[str] = Field(None, description="Additional roadmap description")


class RoadmapInfo(BaseModel):
    """Model for roadmap information."""
    project_id: str = Field(..., description="Project ID")
    milestones: List[Milestone] = Field(..., description="List of milestones")
    current_phase: Optional[int] = Field(None, description="Current phase number")
    total_phases: int = Field(..., description="Total number of phases")
