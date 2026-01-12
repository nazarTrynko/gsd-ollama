"""Codebase mapping API endpoints."""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from ..core.codebase_mapper import CodebaseMapper
from ..core.ollama_client import OllamaClient
from ..utils.path_validator import validate_project_path
from ..utils.error_handler import handle_error

# Default projects directory (must match projects.py)
PROJECTS_DIR = Path("./projects")

router = APIRouter(prefix="/api/projects", tags=["codebase"])

ollama_client = OllamaClient()
codebase_mapper = CodebaseMapper(ollama_client)


@router.post("/{project_id}/codebase/map")
async def map_codebase(
    project_id: str,
    codebase_mapper: CodebaseMapper = Depends(get_codebase_mapper)
):
    """Map and analyze an existing codebase."""
    try:
        project_path = validate_project_path(project_id, PROJECTS_DIR)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Map codebase
        documents = await codebase_mapper.map_codebase(project_path)
        
        return {
            "success": True,
            "documents": documents,
            "project_id": project_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise handle_error(e)


@router.get("/{project_id}/codebase")
async def get_codebase_docs(project_id: str):
    """Get codebase documentation."""
    try:
        project_path = validate_project_path(project_id, PROJECTS_DIR)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        from ..core.file_manager import FileManager
        file_manager = FileManager(project_path)
        codebase_dir = file_manager.planning_dir / "codebase"
        
        if not codebase_dir.exists():
            raise HTTPException(status_code=404, detail="Codebase not mapped. Run map_codebase first.")
        
        documents = {}
        for doc_file in codebase_dir.glob("*.md"):
            documents[doc_file.name] = doc_file.read_text(encoding='utf-8')
        
        return {
            "documents": documents,
            "project_id": project_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise handle_error(e)
