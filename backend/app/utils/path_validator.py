"""Path validation utility for project paths."""

from pathlib import Path
from fastapi import HTTPException


def validate_project_path(project_id: str, projects_dir: Path) -> Path:
    """Validate and resolve project path to prevent path traversal attacks.
    
    Args:
        project_id: Project ID (path string) - can be relative or absolute
        projects_dir: Base projects directory
        
    Returns:
        Resolved and validated Path object
        
    Raises:
        HTTPException: If path is invalid or outside projects directory
    """
    try:
        # Resolve the projects directory to an absolute path
        projects_dir_resolved = projects_dir.resolve()
        
        # Ensure projects directory exists
        projects_dir_resolved.mkdir(parents=True, exist_ok=True)
        
        # Handle both relative and absolute paths
        project_path_input = Path(project_id)
        
        if project_path_input.is_absolute():
            # If absolute, resolve it directly
            project_path = project_path_input.resolve()
        else:
            # If relative, check if it already starts with "projects" prefix
            # This handles legacy project IDs like "projects/video_ideas"
            parts = project_path_input.parts
            if len(parts) > 0 and parts[0] == "projects":
                # Remove the "projects" prefix and use the rest
                project_path_input = Path(*parts[1:])
            # Join with projects_dir first, then resolve
            project_path = (projects_dir_resolved / project_path_input).resolve()
        
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
