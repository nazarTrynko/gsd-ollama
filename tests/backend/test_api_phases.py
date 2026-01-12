"""Integration tests for phase planning and execution API endpoints."""

import pytest
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from app.main import app

client = TestClient(app)


@pytest.fixture
def temp_project(monkeypatch):
    """Create a temporary project with roadmap for testing."""
    temp_dir = tempfile.mkdtemp()
    project_dir = Path(temp_dir) / "test_project"
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Create PROJECT.md
    (project_dir / "PROJECT.md").write_text("# Test Project\n\nA test project.")
    
    # Create ROADMAP.md
    (project_dir / "ROADMAP.md").write_text("""# Roadmap

## Phase 1: Setup
- Task 1.1: Initialize project
- Task 1.2: Configure environment

## Phase 2: Development
- Task 2.1: Implement core features
""")
    
    yield project_dir
    
    shutil.rmtree(temp_dir, ignore_errors=True)


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
            {"task_id": "1", "status": "completed", "output": "Task 1 done"},
            {"task_id": "2", "status": "completed", "output": "Task 2 done"}
        ]
        yield mock_instance


def test_plan_phase(temp_project, mock_phase_planner):
    """Test planning tasks for a phase."""
    project_id = str(temp_project)
    phase_number = 1
    
    response = client.post(f"/api/projects/{project_id}/phases/{phase_number}/plan")
    assert response.status_code == 200
    
    data = response.json()
    assert data["phase_number"] == phase_number
    assert "tasks" in data
    assert isinstance(data["tasks"], list)


def test_plan_phase_nonexistent_project(mock_phase_planner):
    """Test planning phase for nonexistent project."""
    response = client.post("/api/projects/nonexistent/phases/1/plan")
    assert response.status_code == 404


def test_execute_phase(temp_project, mock_task_executor):
    """Test executing tasks for a phase."""
    project_id = str(temp_project)
    phase_number = 1
    
    # First create a plan file
    plan_content = """<?xml version="1.0"?>
<tasks>
    <task id="1">Task 1</task>
    <task id="2">Task 2</task>
</tasks>"""
    (temp_project / "PLAN.md").write_text(plan_content)
    
    execute_data = {}
    
    response = client.post(
        f"/api/projects/{project_id}/phases/{phase_number}/execute",
        json=execute_data
    )
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "results" in data
    assert data["project_id"] == project_id
    assert data["phase_number"] == phase_number


def test_get_progress(temp_project):
    """Test getting execution progress for a phase."""
    project_id = str(temp_project)
    phase_number = 1
    
    response = client.get(f"/api/projects/{project_id}/phases/{phase_number}/progress")
    assert response.status_code == 200
    
    data = response.json()
    assert data["project_id"] == project_id
    assert data["phase_number"] == phase_number
    assert "status" in data
    assert "completed_tasks" in data
    assert "total_tasks" in data
