"""Integration tests for API health and root endpoints."""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root_endpoint():
    """Test the root endpoint returns correct information."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "GSD Ollama API"
    assert data["version"] == "0.1.0"
    assert "docs" in data


def test_health_endpoint():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
