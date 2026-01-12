"""Task management API endpoints."""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from ..core.project_manager import ProjectManager
from ..utils.path_validator import validate_project_path
from ..utils.error_handler import handle_error

# Default projects directory (must match projects.py)
PROJECTS_DIR = Path("./projects")

router = APIRouter(prefix="/api/projects", tags=["tasks"])


@router.get("/{project_id:path}/progress")
async def get_progress(project_id: str):
    """Get overall project progress."""
    try:
        project_path = validate_project_path(project_id, PROJECTS_DIR)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_manager = ProjectManager(project_path)
        
        # Get project info
        project_info = project_manager.get_project_info()
        roadmap = project_manager.get_roadmap()
        state = project_manager.get_state()
        summary = project_manager.get_summary()
        
        return {
            "project_id": project_id,
            "project_info": project_info,
            "has_roadmap": roadmap is not None,
            "has_state": state is not None,
            "has_summary": summary is not None,
            "summary_length": len(summary) if summary else 0
        }
    except HTTPException:
        raise
    except Exception as e:
        raise handle_error(e)
