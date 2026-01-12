"""Project management API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from pathlib import Path
from typing import List
from ..models.project import ProjectCreate, ProjectInfo, ProjectList
from ..core.project_manager import ProjectManager
from ..core.ollama_client import OllamaClient
from ..core.dependencies import get_ollama_client
from ..utils.prompts import NEW_PROJECT_PROMPT
from ..utils.path_validator import validate_project_path
from ..utils.error_handler import handle_error
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/projects", tags=["projects"])

# Default projects directory
PROJECTS_DIR = Path("./projects")
PROJECTS_DIR.mkdir(exist_ok=True)


@router.post("/new", response_model=ProjectInfo)
async def create_project(
    project_data: ProjectCreate,
    ollama_client: OllamaClient = Depends(get_ollama_client)
):
    """Create a new project."""
    try:
        logger.info(f"Creating project: {project_data.name}")
        # Determine project path
        if project_data.project_path:
            project_path = Path(project_data.project_path).resolve()
        else:
            # Create in projects directory
            safe_name = "".join(c for c in project_data.name if c.isalnum() or c in (' ', '-', '_')).strip()
            safe_name = safe_name.replace(' ', '_')
            project_path = (PROJECTS_DIR / safe_name).resolve()
        
        project_path.mkdir(parents=True, exist_ok=True)
        
        # Check if Ollama is available before attempting generation
        try:
            ollama_available = await ollama_client.check_server()
            if not ollama_available:
                logger.warning("Ollama server not available, creating project without AI generation")
                # Create a basic PROJECT.md without Ollama
                basic_project_md = f"# {project_data.name}\n\n{project_data.description}\n"
                if project_data.initial_task:
                    basic_project_md += f"\n## Initial Task\n\n{project_data.initial_task}\n"
                project_manager = ProjectManager(project_path)
                project_manager.file_manager.write_project(basic_project_md)
                project_info = project_manager.get_project_info()
                project_info['id'] = str(project_path.relative_to(PROJECTS_DIR.resolve()))
                return ProjectInfo(**project_info)
        except Exception as e:
            logger.warning(f"Error checking Ollama server: {e}, creating project without AI generation")
            # Create a basic PROJECT.md without Ollama
            basic_project_md = f"# {project_data.name}\n\n{project_data.description}\n"
            if project_data.initial_task:
                basic_project_md += f"\n## Initial Task\n\n{project_data.initial_task}\n"
            project_manager = ProjectManager(project_path)
            project_manager.file_manager.write_project(basic_project_md)
            project_info = project_manager.get_project_info()
            project_info['id'] = str(project_path.relative_to(PROJECTS_DIR.resolve()))
            return ProjectInfo(**project_info)
        
        # Create PROJECT.md using Ollama
        prompt = f"{NEW_PROJECT_PROMPT}\n\nProject Name: {project_data.name}\nDescription: {project_data.description}\n"
        if project_data.initial_task:
            prompt += f"Initial Task: {project_data.initial_task}\n"
        prompt += "\nGenerate the PROJECT.md file:"
        
        try:
            result = await ollama_client.generate(
                prompt=prompt,
                system_prompt="You are an expert project planner. Create comprehensive project documentation."
            )
        except Exception as e:
            logger.error(f"Error generating PROJECT.md with Ollama: {e}, using fallback")
            # Fallback to basic PROJECT.md if Ollama generation fails
            basic_project_md = f"# {project_data.name}\n\n{project_data.description}\n"
            if project_data.initial_task:
                basic_project_md += f"\n## Initial Task\n\n{project_data.initial_task}\n"
            project_manager = ProjectManager(project_path)
            project_manager.file_manager.write_project(basic_project_md)
            project_info = project_manager.get_project_info()
            project_info['id'] = str(project_path.relative_to(PROJECTS_DIR.resolve()))
            return ProjectInfo(**project_info)
        
        # Save PROJECT.md
        project_manager = ProjectManager(project_path)
        project_manager.file_manager.write_project(result['response'])
        
        # Get project info
        project_info = project_manager.get_project_info()
        # Use relative path from PROJECTS_DIR as the ID for consistency
        project_info['id'] = str(project_path.relative_to(PROJECTS_DIR.resolve()))
        
        return ProjectInfo(**project_info)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_error(e)


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
                    # Use relative path from PROJECTS_DIR as the ID
                    project_info['id'] = str(project_dir.relative_to(PROJECTS_DIR.resolve()))
                    projects.append(ProjectInfo(**project_info))
        
        return ProjectList(projects=projects, total=len(projects))
    except HTTPException:
        raise
    except Exception as e:
        raise handle_error(e)


@router.get("/{project_id:path}", response_model=ProjectInfo)
async def get_project(project_id: str):
    """Get project details."""
    try:
        project_path = validate_project_path(project_id, PROJECTS_DIR)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        project_manager = ProjectManager(project_path)
        project_info = project_manager.get_project_info()
        # Use relative path from PROJECTS_DIR as the ID for consistency
        project_info['id'] = str(project_path.relative_to(PROJECTS_DIR.resolve()))
        
        return ProjectInfo(**project_info)
    except HTTPException:
        raise
    except Exception as e:
        raise handle_error(e)


@router.delete("/{project_id:path}")
async def delete_project(project_id: str):
    """Delete a project."""
    try:
        project_path = validate_project_path(project_id, PROJECTS_DIR)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        import shutil
        shutil.rmtree(project_path)
        
        return {"success": True, "message": "Project deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise handle_error(e)
