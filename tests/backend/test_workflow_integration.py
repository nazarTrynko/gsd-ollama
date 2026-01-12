"""End-to-end integration tests for the complete workflow."""

import pytest
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from app.main import app

client = TestClient(app)


@pytest.fixture
def temp_projects_dir(monkeypatch):
    """Create a temporary projects directory for testing."""
    temp_dir = tempfile.mkdtemp()
    projects_dir = Path(temp_dir) / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)
    
    # Monkeypatch the PROJECTS_DIR
    import app.api.projects as projects_module
    original_dir = projects_module.PROJECTS_DIR
    projects_module.PROJECTS_DIR = projects_dir
    
    yield projects_dir
    
    # Restore and cleanup
    projects_module.PROJECTS_DIR = original_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_ollama():
    """Mock Ollama client for the entire workflow."""
    with patch('app.api.projects.ollama_client') as mock_projects, \
         patch('app.api.roadmap.ollama_client') as mock_roadmap, \
         patch('app.api.phases.ollama_client') as mock_phases:
        
        mock_instance = Mock()
        mock_instance.generate.return_value = {
            'response': '# Test Project\n\nThis is a test project.',
            'model': 'llama3.2',
            'done': True
        }
        
        mock_projects.return_value = mock_instance
        mock_roadmap.return_value = mock_instance
        mock_phases.return_value = mock_instance
        
        yield mock_instance


@pytest.fixture
def mock_roadmap_engine():
    """Mock roadmap engine."""
    with patch('app.api.roadmap.roadmap_engine') as mock:
        mock_instance = Mock()
        mock_instance.generate_roadmap.return_value = """# Roadmap

## Phase 1: Setup
- Task 1.1: Initialize project
- Task 1.2: Configure environment

## Phase 2: Development
- Task 2.1: Implement core features
"""
        yield mock_instance


@pytest.fixture
def mock_phase_planner():
    """Mock phase planner."""
    with patch('app.api.phases.phase_planner') as mock:
        mock_instance = Mock()
        mock_instance.plan_phase.return_value = [
            {"id": "1", "description": "Task 1", "status": "pending"},
            {"id": "2", "description": "Task 2", "status": "pending"}
        ]
        yield mock_instance


@pytest.fixture
def mock_task_executor():
    """Mock task executor."""
    with patch('app.api.phases.task_executor') as mock:
        mock_instance = Mock()
        mock_instance.execute_phase.return_value = [
            {"task_id": "1", "status": "completed", "output": "Task 1 done"}
        ]
        yield mock_instance


def test_complete_workflow(
    temp_projects_dir,
    mock_ollama,
    mock_roadmap_engine,
    mock_phase_planner,
    mock_task_executor
):
    """Test the complete workflow: create project -> roadmap -> plan -> execute."""
    
    # Step 1: Create a project
    project_data = {
        "name": "Workflow Test Project",
        "description": "Testing the complete workflow",
        "initial_task": "Set up testing"
    }
    
    create_response = client.post("/api/projects/new", json=project_data)
    assert create_response.status_code == 200
    project_id = create_response.json()["id"]
    project_path = Path(create_response.json()["path"])
    
    assert project_path.exists()
    assert (project_path / "PROJECT.md").exists()
    
    # Step 2: Generate roadmap
    roadmap_response = client.post(f"/api/projects/{project_id}/roadmap", json={})
    assert roadmap_response.status_code == 200
    assert roadmap_response.json()["success"] is True
    
    # Verify roadmap was created
    roadmap_content = roadmap_response.json()["roadmap"]
    assert "Phase 1" in roadmap_content or "Phase" in roadmap_content
    
    # Step 3: Plan phase 1
    plan_response = client.post(f"/api/projects/{project_id}/phases/1/plan")
    assert plan_response.status_code == 200
    plan_data = plan_response.json()
    assert plan_data["phase_number"] == 1
    assert "tasks" in plan_data
    assert len(plan_data["tasks"]) > 0
    
    # Step 4: Get progress (should be idle initially)
    progress_response = client.get(f"/api/projects/{project_id}/phases/1/progress")
    assert progress_response.status_code == 200
    progress_data = progress_response.json()
    assert progress_data["status"] in ["idle", "running", "complete"]
    
    # Step 5: Get overall project progress
    project_progress = client.get(f"/api/projects/{project_id}/progress")
    assert project_progress.status_code == 200
    project_progress_data = project_progress.json()
    assert project_progress_data["project_id"] == project_id
    assert "has_roadmap" in project_progress_data


def test_project_lifecycle(temp_projects_dir, mock_ollama):
    """Test complete project lifecycle: create, list, get, delete."""
    
    # Create project
    project_data = {
        "name": "Lifecycle Test",
        "description": "Testing project lifecycle"
    }
    create_response = client.post("/api/projects/new", json=project_data)
    assert create_response.status_code == 200
    project_id = create_response.json()["id"]
    
    # List projects (should include our project)
    list_response = client.get("/api/projects")
    assert list_response.status_code == 200
    projects = list_response.json()["projects"]
    project_ids = [p["id"] for p in projects]
    assert project_id in project_ids
    
    # Get project details
    get_response = client.get(f"/api/projects/{project_id}")
    assert get_response.status_code == 200
    assert get_response.json()["id"] == project_id
    
    # Delete project
    delete_response = client.delete(f"/api/projects/{project_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["success"] is True
    
    # Verify project is deleted
    get_after_delete = client.get(f"/api/projects/{project_id}")
    assert get_after_delete.status_code == 404
