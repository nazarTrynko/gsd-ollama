"""Path validation utility for project paths."""

from pathlib import Path
from fastapi import HTTPException


def validate_project_path(project_id: str, projects_dir: Path) -> Path:
    """Validate and resolve project path to prevent path traversal attacks.
    
    Args:
        project_id: Project ID (path string)
        projects_dir: Base projects directory
        
    Returns:
        Resolved and validated Path object
        
    Raises:
        HTTPException: If path is invalid or outside projects directory
    """
    try:
        # Resolve the project_id to an absolute path
        project_path = Path(project_id).resolve()
        
        # Resolve the projects directory to an absolute path
        projects_dir_resolved = projects_dir.resolve()
        
        # Ensure projects directory exists
        projects_dir_resolved.mkdir(parents=True, exist_ok=True)
        
        # Check if the project path is within the projects directory
        try:
            # Use relative_to to check if path is within projects_dir
            project_path.relative_to(projects_dir_resolved)
        except ValueError:
            # Path is outside projects directory - security violation
            raise HTTPException(
                status_code=403,
                detail=f"Invalid project path: path must be within projects directory"
            )
        
        return project_path
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid project path: {str(e)}"
        )
