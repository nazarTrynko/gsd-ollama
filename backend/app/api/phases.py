"""Phase planning and execution API endpoints."""

from fastapi import APIRouter, HTTPException, Depends
from pathlib import Path
from ..models.task import TaskPlan, TaskExecute, TaskProgress
from ..core.project_manager import ProjectManager
from ..core.phase_planner import PhasePlanner
from ..core.task_executor import TaskExecutor
from ..core.dependencies import get_phase_planner, get_task_executor
from ..utils.path_validator import validate_project_path
from ..utils.error_handler import handle_error

# Default projects directory (must match projects.py)
PROJECTS_DIR = Path("./projects")

router = APIRouter(prefix="/api/projects", tags=["phases"])


@router.post("/{project_id}/phases/{phase_number}/plan", response_model=TaskPlan)
async def plan_phase(
    project_id: str,
    phase_number: int,
    phase_planner: PhasePlanner = Depends(get_phase_planner)
):
    """Plan tasks for a phase."""
    try:
        # Validate phase_number
        if phase_number <= 0:
            raise HTTPException(status_code=400, detail="Phase number must be positive")
        project_path = validate_project_path(project_id, PROJECTS_DIR)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Plan phase
        tasks = await phase_planner.plan_phase(project_path, phase_number)
        
        return TaskPlan(
            phase_number=phase_number,
            tasks=tasks
        )
    except HTTPException:
        raise
    except Exception as e:
        raise handle_error(e)


@router.post("/{project_id}/phases/{phase_number}/execute")
async def execute_phase(
    project_id: str,
    phase_number: int,
    execute_data: TaskExecute,
    task_executor: TaskExecutor = Depends(get_task_executor)
):
    """Execute tasks for a phase."""
    try:
        project_path = validate_project_path(project_id, PROJECTS_DIR)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get tasks from plan
        project_manager = ProjectManager(project_path)
        plan_content = project_manager.get_plan()
        
        if not plan_content:
            raise HTTPException(status_code=404, detail="Plan not found. Plan phase first.")
        
        # Parse tasks from plan (simplified - in real implementation, would parse XML)
        from ..utils.xml_parser import TaskParser
        tasks = TaskParser.parse_task_xml(plan_content)
        
        # Filter to specific task if provided
        if execute_data.task_id:
            tasks = [t for t in tasks if t.get('id') == execute_data.task_id]
        
        # Initialize progress using FileManager
        file_manager = project_manager.file_manager
        file_manager.write_progress(phase_number, {
            "status": "running",
            "completed_tasks": 0,
            "total_tasks": len(tasks),
            "logs": []
        })
        
        # Execute tasks
        results = await task_executor.execute_phase(project_path, phase_number, tasks)
        
        # Update progress
        file_manager.write_progress(phase_number, {
            "status": "complete",
            "completed_tasks": len(results),
            "total_tasks": len(tasks),
            "logs": []
        })
        
        return {
            "success": True,
            "results": results,
            "project_id": project_id,
            "phase_number": phase_number
        }
    except HTTPException:
        raise
    except Exception as e:
        raise handle_error(e)


@router.get("/{project_id}/phases/{phase_number}/progress", response_model=TaskProgress)
async def get_progress(project_id: str, phase_number: int):
    """Get execution progress for a phase."""
    try:
        project_path = validate_project_path(project_id, PROJECTS_DIR)
        project_manager = ProjectManager(project_path)
        file_manager = project_manager.file_manager
        
        # Read progress from file
        progress = file_manager.read_progress(phase_number)
        if progress is None:
            progress = {
                "status": "idle",
                "completed_tasks": 0,
                "total_tasks": 0,
                "logs": []
            }
        
        return TaskProgress(
            project_id=project_id,
            phase_number=phase_number,
            completed_tasks=progress.get("completed_tasks", 0),
            total_tasks=progress.get("total_tasks", 0),
            status=progress.get("status", "idle"),
            logs=progress.get("logs", [])
        )
    except HTTPException:
        raise
    except Exception as e:
        raise handle_error(e)
