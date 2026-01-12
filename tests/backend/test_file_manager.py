"""Tests for FileManager."""

import pytest
import json
from pathlib import Path
from app.core.file_manager import FileManager


def test_file_manager_initialization(tmp_path):
    """Test FileManager initialization creates .planning directory."""
    fm = FileManager(tmp_path)
    assert fm.planning_dir.exists()
    assert fm.planning_dir.name == ".planning"


def test_read_write_project(tmp_path):
    """Test reading and writing PROJECT.md."""
    fm = FileManager(tmp_path)
    content = "# Test Project\n\nDescription"
    
    fm.write_project(content)
    assert fm.project_file.exists()
    
    result = fm.read_project()
    assert result == content


def test_read_write_progress(tmp_path):
    """Test reading and writing progress."""
    fm = FileManager(tmp_path)
    phase_number = 1
    progress = {
        "status": "running",
        "completed_tasks": 2,
        "total_tasks": 5,
        "logs": ["Task 1 complete", "Task 2 complete"]
    }
    
    fm.write_progress(phase_number, progress)
    assert fm.progress_file.exists()
    
    result = fm.read_progress(phase_number)
    assert result == progress
    assert result["status"] == "running"
    assert result["completed_tasks"] == 2


def test_read_progress_nonexistent(tmp_path):
    """Test reading progress for non-existent phase."""
    fm = FileManager(tmp_path)
    result = fm.read_progress(999)
    assert result is None


def test_multiple_phases_progress(tmp_path):
    """Test storing progress for multiple phases."""
    fm = FileManager(tmp_path)
    
    progress1 = {"status": "complete", "completed_tasks": 3, "total_tasks": 3}
    progress2 = {"status": "running", "completed_tasks": 1, "total_tasks": 5}
    
    fm.write_progress(1, progress1)
    fm.write_progress(2, progress2)
    
    assert fm.read_progress(1) == progress1
    assert fm.read_progress(2) == progress2


def test_get_all_progress(tmp_path):
    """Test getting all progress data."""
    fm = FileManager(tmp_path)
    
    fm.write_progress(1, {"status": "complete"})
    fm.write_progress(2, {"status": "running"})
    
    all_progress = fm.get_all_progress()
    assert "1" in all_progress
    assert "2" in all_progress
    assert all_progress["1"]["status"] == "complete"
    assert all_progress["2"]["status"] == "running"
