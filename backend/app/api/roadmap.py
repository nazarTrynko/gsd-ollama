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


@router.post("/{project_id:path}/roadmap")
async def create_roadmap(
    project_id: str,
    roadmap_data: RoadmapCreate = RoadmapCreate(),
    roadmap_engine: RoadmapEngine = Depends(get_roadmap_engine)
):
    """Create roadmap for a project."""
    try:
        project_path = validate_project_path(project_id, PROJECTS_DIR)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Check if Ollama is available before attempting generation
        try:
            ollama_available = await roadmap_engine.ollama_client.check_server()
            if not ollama_available:
                # Create a basic roadmap without AI
                from ..core.file_manager import FileManager
                file_manager = FileManager(project_path)
                project_content = file_manager.read_project()
                if project_content:
                    basic_roadmap = f"# Roadmap\n\n## Phase 1: Initial Setup\n\nSet up project structure and basic configuration.\n\n## Phase 2: Core Development\n\nImplement core features and functionality.\n\n## Phase 3: Testing & Polish\n\nAdd tests and improve user experience.\n"
                    file_manager.write_roadmap(basic_roadmap)
                    return {
                        "success": True,
                        "roadmap": basic_roadmap,
                        "project_id": project_id
                    }
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(f"Error checking Ollama server: {e}, creating basic roadmap")
        
        # Generate roadmap with Ollama
        try:
            roadmap_content = await roadmap_engine.generate_roadmap(project_path)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Error generating roadmap with Ollama: {e}, using fallback")
            # Fallback to basic roadmap if generation fails
            from ..core.file_manager import FileManager
            file_manager = FileManager(project_path)
            project_content = file_manager.read_project()
            if project_content:
                basic_roadmap = f"# Roadmap\n\n## Phase 1: Initial Setup\n\nSet up project structure and basic configuration.\n\n## Phase 2: Core Development\n\nImplement core features and functionality.\n\n## Phase 3: Testing & Polish\n\nAdd tests and improve user experience.\n"
                file_manager.write_roadmap(basic_roadmap)
                return {
                    "success": True,
                    "roadmap": basic_roadmap,
                    "project_id": project_id
                }
            raise
        
        return {
            "success": True,
            "roadmap": roadmap_content,
            "project_id": project_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise handle_error(e)


@router.get("/{project_id:path}/roadmap")
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
