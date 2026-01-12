"""Phase planning and execution API endpoints."""

from fastapi import APIRouter, HTTPException
from pathlib import Path
from ..models.task import TaskPlan, TaskExecute, TaskProgress
from ..core.project_manager import ProjectManager
from ..core.phase_planner import PhasePlanner
from ..core.task_executor import TaskExecutor
from ..core.ollama_client import OllamaClient

router = APIRouter(prefix="/api/projects", tags=["phases"])

ollama_client = OllamaClient()
phase_planner = PhasePlanner(ollama_client)
task_executor = TaskExecutor(ollama_client)

# Store progress for each project/phase
progress_store = {}


@router.post("/{project_id}/phases/{phase_number}/plan", response_model=TaskPlan)
async def plan_phase(project_id: str, phase_number: int):
    """Plan tasks for a phase."""
    try:
        project_path = Path(project_id)
        if not project_path.exists():
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Plan phase
        tasks = phase_planner.plan_phase(project_path, phase_number)
        
        return TaskPlan(
            phase_number=phase_number,
            tasks=tasks
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{project_id}/phases/{phase_number}/execute")
async def execute_phase(project_id: str, phase_number: int, execute_data: TaskExecute):
    """Execute tasks for a phase."""
    try:
        project_path = Path(project_id)
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
        
        # Initialize progress
        progress_key = f"{project_id}:{phase_number}"
        progress_store[progress_key] = {
            "status": "running",
            "completed_tasks": 0,
            "total_tasks": len(tasks),
            "logs": []
        }
        
        # Execute tasks
        results = task_executor.execute_phase(project_path, phase_number, tasks)
        
        # Update progress
        progress_store[progress_key]["status"] = "complete"
        progress_store[progress_key]["completed_tasks"] = len(results)
        
        return {
            "success": True,
            "results": results,
            "project_id": project_id,
            "phase_number": phase_number
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{project_id}/phases/{phase_number}/progress", response_model=TaskProgress)
async def get_progress(project_id: str, phase_number: int):
    """Get execution progress for a phase."""
    try:
        progress_key = f"{project_id}:{phase_number}"
        progress = progress_store.get(progress_key, {
            "status": "idle",
            "completed_tasks": 0,
            "total_tasks": 0,
            "logs": []
        })
        
        return TaskProgress(
            project_id=project_id,
            phase_number=phase_number,
            completed_tasks=progress["completed_tasks"],
            total_tasks=progress["total_tasks"],
            status=progress["status"],
            logs=progress.get("logs", [])
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
