"""Roadmap API endpoints."""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from ..models.roadmap import RoadmapCreate, RoadmapInfo
from ..core.project_manager import ProjectManager
from ..core.roadmap_engine import RoadmapEngine
from ..core.ollama_client import OllamaClient

router = APIRouter(prefix="/api/projects", tags=["roadmap"])

ollama_client = OllamaClient()
roadmap_engine = RoadmapEngine(ollama_client)


@router.post("/{project_id}/roadmap")
async def create_roadmap(project_id: str, roadmap_data: RoadmapCreate):
    """Create roadmap for a project."""
    try:
        project_path = Path(project_id)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Generate roadmap
        roadmap_content = roadmap_engine.generate_roadmap(project_path)
        
        return {
            "success": True,
            "roadmap": roadmap_content,
            "project_id": project_id
        }
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/roadmap")
async def get_roadmap(project_id: str):
    """Get roadmap for a project."""
    try:
        project_path = Path(project_id)
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
        raise HTTPException(status_code=500, detail=str(e))
