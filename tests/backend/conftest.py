"""Pytest configuration and fixtures for backend tests."""

import pytest
import tempfile
import shutil
from pathlib import Path
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch

from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def temp_projects_dir():
    """Create a temporary projects directory for testing."""
    temp_dir = tempfile.mkdtemp()
    projects_dir = Path(temp_dir) / "projects"
    projects_dir.mkdir(parents=True, exist_ok=True)
    
    yield projects_dir
    
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client for testing."""
    with patch('app.core.ollama_client.OllamaClient') as mock:
        mock_instance = Mock()
        mock_instance.generate.return_value = {
            'response': '# Test Project\n\nThis is a test project.',
            'model': 'llama3.2',
            'done': True
        }
        mock.return_value = mock_instance
        yield mock_instance


@pytest.fixture
def sample_project_data():
    """Sample project data for testing."""
    return {
        "name": "Test Project",
        "description": "A test project for integration testing",
        "initial_task": "Set up testing infrastructure"
    }
