"""Integration tests for project management API endpoints."""

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
    
    # Monkeypatch the PROJECTS_DIR in the projects router
    import app.api.projects as projects_module
    original_dir = projects_module.PROJECTS_DIR
    projects_module.PROJECTS_DIR = projects_dir
    
    yield projects_dir
    
    # Restore and cleanup
    projects_module.PROJECTS_DIR = original_dir
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_ollama():
    """Mock Ollama client."""
    with patch('app.api.projects.ollama_client') as mock:
        mock_instance = Mock()
        mock_instance.generate.return_value = {
            'response': '# Test Project\n\nThis is a test project for integration testing.\n\n## Goals\n\n- Test the API\n- Verify integration\n',
            'model': 'llama3.2',
            'done': True
        }
        yield mock_instance


def test_create_project(temp_projects_dir, mock_ollama):
    """Test creating a new project."""
    project_data = {
        "name": "Integration Test Project",
        "description": "A project for testing integration",
        "initial_task": "Write tests"
    }
    
    response = client.post("/api/projects/new", json=project_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "id" in data
    assert data["name"] == "Integration_Test_Project"
    assert "path" in data
    
    # Verify project directory was created
    project_path = Path(data["path"])
    assert project_path.exists()
    assert (project_path / "PROJECT.md").exists()


def test_list_projects(temp_projects_dir, mock_ollama):
    """Test listing all projects."""
    # Create a project first
    project_data = {
        "name": "Test Project 1",
        "description": "First test project"
    }
    create_response = client.post("/api/projects/new", json=project_data)
    assert create_response.status_code == 200
    
    # List projects
    response = client.get("/api/projects")
    assert response.status_code == 200
    
    data = response.json()
    assert "projects" in data
    assert "total" in data
    assert data["total"] >= 1
    assert len(data["projects"]) >= 1


def test_get_project(temp_projects_dir, mock_ollama):
    """Test getting a specific project."""
    # Create a project first
    project_data = {
        "name": "Test Project Get",
        "description": "Project for get test"
    }
    create_response = client.post("/api/projects/new", json=project_data)
    assert create_response.status_code == 200
    project_id = create_response.json()["id"]
    
    # Get the project
    response = client.get(f"/api/projects/{project_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["id"] == project_id
    assert "name" in data
    assert "path" in data


def test_get_nonexistent_project():
    """Test getting a project that doesn't exist."""
    response = client.get("/api/projects/nonexistent/project/path")
    assert response.status_code == 404


def test_delete_project(temp_projects_dir, mock_ollama):
    """Test deleting a project."""
    # Create a project first
    project_data = {
        "name": "Test Project Delete",
        "description": "Project for delete test"
    }
    create_response = client.post("/api/projects/new", json=project_data)
    assert create_response.status_code == 200
    project_id = create_response.json()["id"]
    project_path = Path(create_response.json()["path"])
    
    # Verify project exists
    assert project_path.exists()
    
    # Delete the project
    response = client.delete(f"/api/projects/{project_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    
    # Verify project was deleted
    assert not project_path.exists()
