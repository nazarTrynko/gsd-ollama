"""Project management API endpoints."""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from typing import List
from ..models.project import ProjectCreate, ProjectInfo, ProjectList
from ..core.project_manager import ProjectManager
from ..core.ollama_client import OllamaClient
from ..core.roadmap_engine import RoadmapEngine
from ..utils.prompts import NEW_PROJECT_PROMPT

router = APIRouter(prefix="/api/projects", tags=["projects"])

# Default projects directory
PROJECTS_DIR = Path("./projects")
PROJECTS_DIR.mkdir(exist_ok=True)

ollama_client = OllamaClient()


@router.post("/new", response_model=ProjectInfo)
async def create_project(project_data: ProjectCreate):
    """Create a new project."""
    try:
        # Determine project path
        if project_data.project_path:
            project_path = Path(project_data.project_path)
        else:
            # Create in projects directory
            safe_name = "".join(c for c in project_data.name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            project_path = PROJECTS_DIR / safe_name
        
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Create PROJECT.md using Ollama
        prompt = f"{NEW_PROJECT_PROMPT}\n\nProject Name: {project_data.name}\nDescription: {project_data.description}\n"
        if project_data.initial_task:
            prompt += f"Initial Task: {project_data.initial_task}\n"
        prompt += "\nGenerate the PROJECT.md file:"
        
        result = ollama_client.generate(
            prompt=prompt,
            system_prompt="You are an expert project planner. Create comprehensive project documentation."
        )
        
        # Save PROJECT.md
        project_manager = ProjectManager(project_path)
        project_manager.file_manager.write_project(result['response'])
        
        # Get project info
        project_info = project_manager.get_project_info()
        project_info['id'] = str(project_path)
        
        return ProjectInfo(**project_info)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("", response_model=ProjectList)
async def list_projects():
    """List all projects."""
    try:
        projects = []
        
        if PROJECTS_DIR.exists():
            for project_dir in PROJECTS_DIR.iterdir():
                if project_dir.is_dir():
                    project_manager = ProjectManager(project_dir)
                    project_info = project_manager.get_project_info()
                    project_info['id'] = str(project_dir)
                    projects.append(ProjectInfo(**project_info))
        
        return ProjectList(projects=projects, total=len(projects))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}", response_model=ProjectInfo)
async def get_project(project_id: str):
    """Get project details."""
    try:
        project_path = Path(project_id)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_manager = ProjectManager(project_path)
        project_info = project_manager.get_project_info()
        project_info['id'] = str(project_path)
        
        return ProjectInfo(**project_info)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{project_id}")
async def delete_project(project_id: str):
    """Delete a project."""
    try:
        project_path = Path(project_id)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Only allow deletion from projects directory for safety
        if not str(project_path).startswith(str(PROJECTS_DIR)):
            raise HTTPException(status_code=403, detail="Can only delete projects from projects directory")
        
        import shutil
        shutil.rmtree(project_path)
        
        return {"success": True, "message": "Project deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
