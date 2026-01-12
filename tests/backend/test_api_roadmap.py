"""Integration tests for roadmap API endpoints."""

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
    """Create a temporary project for testing."""
    temp_dir = tempfile.mkdtemp()
    project_dir = Path(temp_dir) / "test_project"
    project_dir.mkdir(parents=True, exist_ok=True)
    
    # Create a basic PROJECT.md
    (project_dir / "PROJECT.md").write_text("# Test Project\n\nA test project.")
    
    yield project_dir
    
    shutil.rmtree(temp_dir, ignore_errors=True)


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
- Task 2.2: Add tests
"""
        yield mock_instance


def test_create_roadmap(temp_project, mock_roadmap_engine):
    """Test creating a roadmap for a project."""
    project_id = str(temp_project)
    roadmap_data = {}
    
    response = client.post(f"/api/projects/{project_id}/roadmap", json=roadmap_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["success"] is True
    assert "roadmap" in data
    assert data["project_id"] == project_id


def test_get_roadmap(temp_project):
    """Test getting a roadmap for a project."""
    project_id = str(temp_project)
    
    # First create a roadmap file
    roadmap_content = "# Roadmap\n\n## Phase 1: Setup"
    (temp_project / "ROADMAP.md").write_text(roadmap_content)
    
    # Get the roadmap
    response = client.get(f"/api/projects/{project_id}/roadmap")
    assert response.status_code == 200
    
    data = response.json()
    assert "roadmap" in data
    assert data["project_id"] == project_id


def test_get_nonexistent_roadmap(temp_project):
    """Test getting a roadmap that doesn't exist."""
    project_id = str(temp_project)
    
    response = client.get(f"/api/projects/{project_id}/roadmap")
    assert response.status_code == 404


def test_create_roadmap_nonexistent_project():
    """Test creating a roadmap for a project that doesn't exist."""
    response = client.post("/api/projects/nonexistent/roadmap", json={})
    assert response.status_code == 404
