"""Enhanced end-to-end API tests for complete workflows."""

import pytest
import tempfile
import shutil
import json
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, Mock
from app.main import app

client = TestClient(app)


@pytest.fixture
def temp_projects_dir(monkeypatch):
    """Create a temporary projects directory for testing."""
    temp_dir = tempfile.mkdtemp()
    projects_dir = Path(temp_dir) / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)
    
    # Monkeypatch PROJECTS_DIR in all API modules
    import app.api.projects as projects_module
    import app.api.roadmap as roadmap_module
    import app.api.phases as phases_module
    import app.api.tasks as tasks_module
    import app.api.codebase as codebase_module
    
    original_projects = projects_module.PROJECTS_DIR
    original_roadmap = roadmap_module.PROJECTS_DIR
    original_phases = phases_module.PROJECTS_DIR
    original_tasks = tasks_module.PROJECTS_DIR
    original_codebase = codebase_module.PROJECTS_DIR
    
    projects_module.PROJECTS_DIR = projects_dir
    roadmap_module.PROJECTS_DIR = projects_dir
    phases_module.PROJECTS_DIR = projects_dir
    tasks_module.PROJECTS_DIR = projects_dir
    codebase_module.PROJECTS_DIR = projects_dir
    
    yield projects_dir
    
    # Restore and cleanup
    projects_module.PROJECTS_DIR = original_projects
    roadmap_module.PROJECTS_DIR = original_roadmap
    phases_module.PROJECTS_DIR = original_phases
    tasks_module.PROJECTS_DIR = original_tasks
    codebase_module.PROJECTS_DIR = original_codebase
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client with async methods."""
    mock_instance = AsyncMock()
    mock_instance.check_server.return_value = True
    mock_instance.list_models.return_value = ["llama3.2", "llama3.1"]
    mock_instance.default_model = "llama3.2"
    mock_instance.base_url = "http://localhost:11434"
    mock_instance.generate.return_value = {
        'response': '# Test Project\n\nThis is a test project description.',
        'model': 'llama3.2',
        'tokens': {'prompt': 10, 'completion': 20, 'total': 30},
        'done': True
    }
    
    with patch('app.core.dependencies.get_ollama_client', return_value=mock_instance):
        yield mock_instance


@pytest.fixture
def mock_roadmap_engine():
    """Mock roadmap engine."""
    mock_instance = AsyncMock()
    mock_instance.generate_roadmap.return_value = """# Roadmap

## Milestone v1.0

### Phase 1: Setup
Initialize project structure and development environment.

### Phase 2: Core Features
Implement main functionality.

### Phase 3: Testing & Polish
Add tests and improve user experience.
"""
    
    with patch('app.core.dependencies.get_roadmap_engine', return_value=mock_instance):
        yield mock_instance


@pytest.fixture
def mock_phase_planner():
    """Mock phase planner."""
    mock_instance = AsyncMock()
    mock_instance.plan_phase.return_value = [
        {
            "id": "task-1-1-abc12345",
            "name": "Initialize project structure",
            "type": "auto",
            "action": "Create project directory structure",
            "status": "pending"
        },
        {
            "id": "task-1-2-def67890",
            "name": "Set up development environment",
            "type": "auto",
            "action": "Configure development tools",
            "status": "pending"
        }
    ]
    
    with patch('app.core.dependencies.get_phase_planner', return_value=mock_instance):
        yield mock_instance


@pytest.fixture
def mock_task_executor():
    """Mock task executor."""
    mock_instance = AsyncMock()
    mock_instance.execute_phase.return_value = [
        {
            "task_id": "task-1-1-abc12345",
            "task_name": "Initialize project structure",
            "status": "complete",
            "result": "Project structure created successfully"
        },
        {
            "task_id": "task-1-2-def67890",
            "task_name": "Set up development environment",
            "status": "complete",
            "result": "Development environment configured"
        }
    ]
    
    with patch('app.core.dependencies.get_task_executor', return_value=mock_instance):
        yield mock_instance


@pytest.mark.e2e
@pytest.mark.api_e2e
def test_complete_workflow_e2e(
    temp_projects_dir,
    mock_ollama_client,
    mock_roadmap_engine,
    mock_phase_planner,
    mock_task_executor
):
    """Test complete workflow: create → roadmap → plan → execute → verify."""
    
    # Step 1: Create project
    project_data = {
        "name": "E2E Test Project",
        "description": "Testing complete e2e workflow",
        "initial_task": "Set up e2e testing"
    }
    
    create_response = client.post("/api/projects/new", json=project_data)
    assert create_response.status_code == 200, f"Expected 200, got {create_response.status_code}: {create_response.text}"
    project_info = create_response.json()
    project_path = Path(project_info["path"])
    
    # Verify project files created
    assert project_path.exists()
    planning_dir = project_path / ".planning"
    assert planning_dir.exists()
    assert (planning_dir / "PROJECT.md").exists()
    
    # Step 2: Generate roadmap
    # Use the full project path as project_id (as returned by the API)
    from urllib.parse import quote
    project_id = str(project_path)
    encoded_project_id = quote(project_id, safe='')
    roadmap_response = client.post(
        f"/api/projects/{encoded_project_id}/roadmap",
        json={"project_id": project_id}
    )
    assert roadmap_response.status_code == 200
    roadmap_data = roadmap_response.json()
    assert roadmap_data["success"] is True
    assert "roadmap" in roadmap_data
    
    # Verify roadmap file created
    assert (planning_dir / "ROADMAP.md").exists()
    
    # Step 3: Plan phase 1
    plan_response = client.post(f"/api/projects/{encoded_project_id}/phases/1/plan")
    assert plan_response.status_code == 200
    plan_data = plan_response.json()
    assert plan_data["phase_number"] == 1
    assert "tasks" in plan_data
    assert len(plan_data["tasks"]) > 0
    
    # Verify plan file created
    assert (planning_dir / "PLAN.md").exists()
    
    # Step 4: Get progress (should be idle initially)
    progress_response = client.get(f"/api/projects/{encoded_project_id}/phases/1/progress")
    assert progress_response.status_code == 200
    progress_data = progress_response.json()
    assert progress_data["status"] in ["idle", "running", "complete"]
    assert progress_data["phase_number"] == 1
    
    # Step 5: Execute phase 1
    execute_response = client.post(
        f"/api/projects/{encoded_project_id}/phases/1/execute",
        json={
            "project_id": project_id,
            "phase_number": 1
        }
    )
    assert execute_response.status_code == 200
    execute_data = execute_response.json()
    assert execute_data["success"] is True
    assert "results" in execute_data
    assert len(execute_data["results"]) > 0
    
    # Verify progress updated
    progress_after = client.get(f"/api/projects/{encoded_project_id}/phases/1/progress")
    assert progress_after.status_code == 200
    progress_after_data = progress_after.json()
    assert progress_after_data["completed_tasks"] > 0
    
    # Verify summary file created
    assert (planning_dir / "SUMMARY.md").exists()
    
    # Step 6: Get overall project progress
    project_progress = client.get(f"/api/projects/{encoded_project_id}/progress")
    assert project_progress.status_code == 200
    project_progress_data = project_progress.json()
    assert project_progress_data["project_id"] == project_id
    assert project_progress_data["has_roadmap"] is True
    assert project_progress_data["has_summary"] is True
    
    # Step 7: Delete project
    delete_response = client.delete(f"/api/projects/{encoded_project_id}")
    assert delete_response.status_code == 200
    assert delete_response.json()["success"] is True
    
    # Verify project deleted
    get_after_delete = client.get(f"/api/projects/{encoded_project_id}")
    assert get_after_delete.status_code == 404


@pytest.mark.e2e
@pytest.mark.api_e2e
def test_error_handling_ollama_failure(temp_projects_dir):
    """Test error handling when Ollama connection fails."""
    
    # Mock Ollama client to raise connection error
    mock_ollama = AsyncMock()
    mock_ollama.check_server.return_value = False
    mock_ollama.generate.side_effect = Exception("Ollama connection failed")
    
    with patch('app.core.dependencies.get_ollama_client', return_value=mock_ollama):
        project_data = {
            "name": "Ollama Failure Test",
            "description": "Testing Ollama failure handling"
        }
        
        # Project creation should handle Ollama errors gracefully
        response = client.post("/api/projects/new", json=project_data)
        # Should either succeed (if error handled) or return appropriate error
        assert response.status_code in [200, 500, 503]


@pytest.mark.e2e
@pytest.mark.api_e2e
def test_error_handling_invalid_project(temp_projects_dir):
    """Test error handling with invalid project ID."""
    
    # Try to get non-existent project
    response = client.get("/api/projects/nonexistent-project")
    assert response.status_code in [404, 403]  # 403 if path validation fails
    
    # Try to generate roadmap for non-existent project
    response = client.post("/api/projects/nonexistent-project/roadmap", json={})
    assert response.status_code in [404, 403]
    
    # Try to plan phase for non-existent project
    response = client.post("/api/projects/nonexistent-project/phases/1/plan")
    assert response.status_code in [404, 403]


@pytest.mark.e2e
@pytest.mark.api_e2e
def test_error_handling_missing_roadmap(
    temp_projects_dir,
    mock_ollama_client,
    mock_phase_planner
):
    """Test error handling when roadmap doesn't exist."""
    
    # Create project
    project_data = {
        "name": "No Roadmap Test",
        "description": "Testing without roadmap"
    }
    create_response = client.post("/api/projects/new", json=project_data)
    assert create_response.status_code == 200
    project_id = create_response.json()["id"]
    
    # Try to plan phase without roadmap
    plan_response = client.post(f"/api/projects/{project_id}/phases/1/plan")
    assert plan_response.status_code in [400, 404]  # Should fail gracefully


@pytest.mark.e2e
@pytest.mark.api_e2e
def test_error_handling_invalid_phase_number(
    temp_projects_dir,
    mock_ollama_client,
    mock_roadmap_engine
):
    """Test error handling with invalid phase number."""
    
    # Create project and roadmap
    project_data = {
        "name": "Invalid Phase Test",
        "description": "Testing invalid phase numbers"
    }
    create_response = client.post("/api/projects/new", json=project_data)
    assert create_response.status_code == 200
    project_id = create_response.json()["id"]
    
    roadmap_response = client.post(
        f"/api/projects/{project_id}/roadmap",
        json={"project_id": project_id}
    )
    assert roadmap_response.status_code == 200
    
    # Try to plan non-existent phase
    plan_response = client.post(f"/api/projects/{project_id}/phases/999/plan")
    assert plan_response.status_code in [400, 404]
    
    # Try to execute non-existent phase
    execute_response = client.post(
        f"/api/projects/{project_id}/phases/999/execute",
        json={"project_id": project_id, "phase_number": 999}
    )
    assert execute_response.status_code in [400, 404]


@pytest.mark.e2e
@pytest.mark.api_e2e
def test_edge_case_special_characters(
    temp_projects_dir,
    mock_ollama_client
):
    """Test creating project with special characters in name."""
    
    project_data = {
        "name": "Test Project @#$%^&*()",
        "description": "Testing special characters"
    }
    
    response = client.post("/api/projects/new", json=project_data)
    # Should sanitize name or handle gracefully
    assert response.status_code in [200, 400]
    
    if response.status_code == 200:
        project_id = response.json()["id"]
        # Verify project was created with sanitized name
        get_response = client.get(f"/api/projects/{project_id}")
        assert get_response.status_code == 200


@pytest.mark.e2e
@pytest.mark.api_e2e
def test_edge_case_multiple_projects(
    temp_projects_dir,
    mock_ollama_client
):
    """Test creating and managing multiple projects."""
    
    projects = []
    
    # Create multiple projects
    for i in range(3):
        project_data = {
            "name": f"Multi Project {i+1}",
            "description": f"Testing multiple projects - {i+1}"
        }
        response = client.post("/api/projects/new", json=project_data)
        assert response.status_code == 200
        projects.append(response.json()["id"])
    
    # List all projects
    list_response = client.get("/api/projects")
    assert list_response.status_code == 200
    all_projects = list_response.json()["projects"]
    assert len(all_projects) >= 3
    
    # Verify all created projects are in the list
    project_ids = [p["id"] for p in all_projects]
    for project_id in projects:
        assert project_id in project_ids
    
    # Clean up
    for project_id in projects:
        client.delete(f"/api/projects/{project_id}")


@pytest.mark.e2e
@pytest.mark.api_e2e
def test_progress_persistence(
    temp_projects_dir,
    mock_ollama_client,
    mock_roadmap_engine,
    mock_phase_planner,
    mock_task_executor
):
    """Test that progress persists across requests."""
    
    # Create project and roadmap
    project_data = {
        "name": "Progress Persistence Test",
        "description": "Testing progress persistence"
    }
    create_response = client.post("/api/projects/new", json=project_data)
    assert create_response.status_code == 200
    project_id = create_response.json()["id"]
    
    roadmap_response = client.post(
        f"/api/projects/{project_id}/roadmap",
        json={"project_id": project_id}
    )
    assert roadmap_response.status_code == 200
    
    # Plan phase
    plan_response = client.post(f"/api/projects/{project_id}/phases/1/plan")
    assert plan_response.status_code == 200
    
    # Execute phase
    execute_response = client.post(
        f"/api/projects/{project_id}/phases/1/execute",
        json={"project_id": project_id, "phase_number": 1}
    )
    assert execute_response.status_code == 200
    
    # Get progress immediately
    progress1 = client.get(f"/api/projects/{project_id}/phases/1/progress")
    assert progress1.status_code == 200
    progress_data1 = progress1.json()
    
    # Get progress again (should be same or updated)
    progress2 = client.get(f"/api/projects/{project_id}/phases/1/progress")
    assert progress2.status_code == 200
    progress_data2 = progress2.json()
    
    # Progress should be consistent
    assert progress_data2["phase_number"] == progress_data1["phase_number"]
    assert progress_data2["total_tasks"] == progress_data1["total_tasks"]
    
    # Verify progress file exists
    project_path = Path(project_id)
    progress_file = project_path / ".planning" / "PROGRESS.json"
    assert progress_file.exists()
    
    # Verify progress file content
    with open(progress_file) as f:
        progress_content = json.load(f)
        assert "1" in progress_content  # Phase 1 should be in progress file


@pytest.mark.e2e
@pytest.mark.api_e2e
def test_path_validation_edge_cases(temp_projects_dir):
    """Test path validation with various edge cases."""
    
    # Test path traversal attempt
    malicious_paths = [
        "../../etc/passwd",
        "../projects/../etc",
        "/etc/passwd",
        "projects/../../root"
    ]
    
    for malicious_path in malicious_paths:
        response = client.get(f"/api/projects/{malicious_path}")
        # Should reject with 403
        assert response.status_code == 403, f"Path {malicious_path} should be rejected"
    
    # Test valid paths
    valid_path = str(temp_projects_dir / "valid_project")
    Path(valid_path).mkdir(parents=True, exist_ok=True)
    (Path(valid_path) / ".planning").mkdir(exist_ok=True)
    (Path(valid_path) / ".planning" / "PROJECT.md").write_text("# Test")
    
    response = client.get(f"/api/projects/{valid_path}")
    # Should work if path is within projects directory
    assert response.status_code in [200, 404]


@pytest.mark.e2e
@pytest.mark.api_e2e
def test_file_persistence_verification(
    temp_projects_dir,
    mock_ollama_client,
    mock_roadmap_engine,
    mock_phase_planner,
    mock_task_executor
):
    """Test that all files are properly persisted."""
    
    # Create project
    project_data = {
        "name": "File Persistence Test",
        "description": "Testing file persistence"
    }
    create_response = client.post("/api/projects/new", json=project_data)
    assert create_response.status_code == 200
    project_id = create_response.json()["id"]
    project_path = Path(project_id)
    planning_dir = project_path / ".planning"
    
    # Verify PROJECT.md exists
    assert (planning_dir / "PROJECT.md").exists()
    
    # Generate roadmap
    roadmap_response = client.post(
        f"/api/projects/{project_id}/roadmap",
        json={"project_id": project_id}
    )
    assert roadmap_response.status_code == 200
    
    # Verify ROADMAP.md exists
    assert (planning_dir / "ROADMAP.md").exists()
    roadmap_content = (planning_dir / "ROADMAP.md").read_text()
    assert len(roadmap_content) > 0
    
    # Plan phase
    plan_response = client.post(f"/api/projects/{project_id}/phases/1/plan")
    assert plan_response.status_code == 200
    
    # Verify PLAN.md exists
    assert (planning_dir / "PLAN.md").exists()
    plan_content = (planning_dir / "PLAN.md").read_text()
    assert len(plan_content) > 0
    
    # Execute phase
    execute_response = client.post(
        f"/api/projects/{project_id}/phases/1/execute",
        json={"project_id": project_id, "phase_number": 1}
    )
    assert execute_response.status_code == 200
    
    # Verify SUMMARY.md exists
    assert (planning_dir / "SUMMARY.md").exists()
    summary_content = (planning_dir / "SUMMARY.md").read_text()
    assert len(summary_content) > 0
    
    # Verify PROGRESS.json exists
    assert (planning_dir / "PROGRESS.json").exists()
    with open(planning_dir / "PROGRESS.json") as f:
        progress_data = json.load(f)
        assert "1" in progress_data  # Phase 1 progress should be stored
