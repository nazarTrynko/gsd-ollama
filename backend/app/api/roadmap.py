"""Roadmap API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from pathlib import Path
from ..models.roadmap import RoadmapCreate, RoadmapInfo
from ..core.project_manager import ProjectManager
from ..core.roadmap_engine import RoadmapEngine
from ..core.dependencies import get_roadmap_engine
from ..utils.path_validator import validate_project_path
from ..utils.error_handler import handle_error

# Default projects directory (must match projects.py)
PROJECTS_DIR = Path("./projects")

router = APIRouter(prefix="/api/projects", tags=["roadmap"])


@router.post("/{project_id}/roadmap")
async def create_roadmap(
    project_id: str,
    roadmap_data: RoadmapCreate,
    roadmap_engine: RoadmapEngine = Depends(get_roadmap_engine)
):
    """Create roadmap for a project."""
    try:
        project_path = validate_project_path(project_id, PROJECTS_DIR)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Generate roadmap
        roadmap_content = await roadmap_engine.generate_roadmap(project_path)
        
        return {
            "success": True,
            "roadmap": roadmap_content,
            "project_id": project_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise handle_error(e)


@router.get("/{project_id}/roadmap")
async def get_roadmap(project_id: str):
    """Get roadmap for a project."""
    try:
        project_path = validate_project_path(project_id, PROJECTS_DIR)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_manager = ProjectManager(project_path)
        roadmap_content = project_manager.get_roadmap()
        
        if not roadmap_content:
            raise HTTPException(status_code=404, detail="Roadmap not found. Create roadmap first.")
        
        return {
            "roadmap": roadmap_content,
            "project_id": project_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise handle_error(e)
