"""Codebase mapping API endpoints."""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from ..core.codebase_mapper import CodebaseMapper
from ..core.ollama_client import OllamaClient

router = APIRouter(prefix="/api/projects", tags=["codebase"])

ollama_client = OllamaClient()
codebase_mapper = CodebaseMapper(ollama_client)


@router.post("/{project_id}/codebase/map")
async def map_codebase(project_id: str):
    """Map and analyze an existing codebase."""
    try:
        project_path = Path(project_id)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Map codebase
        documents = codebase_mapper.map_codebase(project_path)
        
        return {
            "success": True,
            "documents": documents,
            "project_id": project_id
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/codebase")
async def get_codebase_docs(project_id: str):
    """Get codebase documentation."""
    try:
        project_path = Path(project_id)
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
        raise HTTPException(status_code=500, detail=str(e))
