"""Tests for path validator utility."""

import pytest
from pathlib import Path
from fastapi import HTTPException
from app.utils.path_validator import validate_project_path


def test_validate_project_path_valid(tmp_path):
    """Test that valid project paths are accepted."""
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    project_dir = projects_dir / "test_project"
    project_dir.mkdir()
    
    result = validate_project_path(str(project_dir), projects_dir)
    assert result == project_dir.resolve()


def test_validate_project_path_outside_directory(tmp_path):
    """Test that paths outside projects directory are rejected."""
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    outside_dir = tmp_path / "outside"
    outside_dir.mkdir()
    
    with pytest.raises(HTTPException) as exc_info:
        validate_project_path(str(outside_dir), projects_dir)
    
    assert exc_info.value.status_code == 403


def test_validate_project_path_traversal_attack(tmp_path):
    """Test that path traversal attacks are prevented."""
    projects_dir = tmp_path / "projects"
    projects_dir.mkdir()
    
    # Try to access parent directory
    malicious_path = str(projects_dir / "../etc/passwd")
    
    with pytest.raises(HTTPException) as exc_info:
        validate_project_path(malicious_path, projects_dir)
    
    assert exc_info.value.status_code == 403


def test_validate_project_path_creates_directory(tmp_path):
    """Test that projects directory is created if it doesn't exist."""
    projects_dir = tmp_path / "projects"
    project_dir = projects_dir / "new_project"
    
    # Should not raise even though projects_dir doesn't exist yet
    result = validate_project_path(str(project_dir), projects_dir)
    assert projects_dir.exists()
    assert result == project_dir.resolve()
