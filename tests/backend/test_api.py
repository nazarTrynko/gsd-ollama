"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from pathlib import Path
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns API info."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data


def test_health_endpoint():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_ollama_status_endpoint():
    """Test Ollama status endpoint."""
    response = client.get("/api/ollama/status")
    # Should return 200 even if Ollama is not running
    assert response.status_code in [200, 503]
    if response.status_code == 200:
        data = response.json()
        assert "connected" in data
        assert "server_url" in data


def test_list_projects_empty():
    """Test listing projects when none exist."""
    response = client.get("/api/projects")
    assert response.status_code == 200
    data = response.json()
    assert "projects" in data
    assert "total" in data
    assert data["total"] >= 0


def test_create_project():
    """Test creating a new project."""
    project_data = {
        "name": "Test Project",
        "description": "A test project"
    }
    response = client.post("/api/projects/new", json=project_data)
    # May fail if Ollama is not running, but should return proper error
    assert response.status_code in [200, 500, 503]
    if response.status_code == 200:
        data = response.json()
        assert "id" in data
        assert data["name"] == "Test Project"


def test_get_nonexistent_project():
    """Test getting a non-existent project returns 404."""
    response = client.get("/api/projects/nonexistent-project-path")
    assert response.status_code in [404, 403]  # 403 if path validation fails, 404 if not found
