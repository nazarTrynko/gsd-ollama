"""Integration tests for Ollama API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, Mock
from app.main import app

client = TestClient(app)


@pytest.fixture
def mock_ollama_client():
    """Mock Ollama client."""
    with patch('app.api.ollama.ollama_client') as mock:
        mock_instance = Mock()
        mock_instance.generate.return_value = {
            'response': 'Test response from Ollama',
            'model': 'llama3.2',
            'done': True
        }
        mock_instance.list_models.return_value = ['llama3.2', 'codellama']
        mock_instance.check_server.return_value = True
        mock_instance.base_url = 'http://localhost:11434'
        mock_instance.default_model = 'llama3.2'
        yield mock_instance


def test_get_status(mock_ollama_client):
    """Test Ollama server status."""
    response = client.get("/api/ollama/status")
    assert response.status_code == 200
    
    data = response.json()
    assert "connected" in data
    assert "server_url" in data
    assert "default_model" in data


def test_list_models(mock_ollama_client):
    """Test listing available Ollama models."""
    response = client.get("/api/ollama/models")
    assert response.status_code == 200
    
    data = response.json()
    assert "models" in data
    assert isinstance(data["models"], list)
    assert len(data["models"]) > 0
    assert "default" in data
