"""File manager for .planning/ directory operations."""

import json
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime


class FileManager:
    """Manages .planning/ directory and project state files."""
    
    def __init__(self, project_path: Path):
        """Initialize file manager for a project.
        
        Args:
            project_path: Path to the project root directory
        """
        self.project_path = Path(project_path)
        self.planning_dir = self.project_path / ".planning"
        self.planning_dir.mkdir(exist_ok=True)
        
        # Planning file paths
        self.project_file = self.planning_dir / "PROJECT.md"
        self.roadmap_file = self.planning_dir / "ROADMAP.md"
        self.state_file = self.planning_dir / "STATE.md"
        self.plan_file = self.planning_dir / "PLAN.md"
        self.summary_file = self.planning_dir / "SUMMARY.md"
        self.issues_file = self.planning_dir / "ISSUES.md"
        self.progress_file = self.planning_dir / "PROGRESS.json"
        self.todos_dir = self.planning_dir / "todos"
        self.todos_dir.mkdir(exist_ok=True)
    
    def read_project(self) -> Optional[str]:
        """Read PROJECT.md file."""
        if self.project_file.exists():
            return self.project_file.read_text(encoding='utf-8')
        return None
    
    def write_project(self, content: str) -> None:
        """Write PROJECT.md file."""
        self.project_file.write_text(content, encoding='utf-8')
    
    def read_roadmap(self) -> Optional[str]:
        """Read ROADMAP.md file."""
        if self.roadmap_file.exists():
            return self.roadmap_file.read_text(encoding='utf-8')
        return None
    
    def write_roadmap(self, content: str) -> None:
        """Write ROADMAP.md file."""
        self.roadmap_file.write_text(content, encoding='utf-8')
    
    def read_state(self) -> Optional[str]:
        """Read STATE.md file."""
        if self.state_file.exists():
            return self.state_file.read_text(encoding='utf-8')
        return None
    
    def write_state(self, content: str) -> None:
        """Write STATE.md file."""
        self.state_file.write_text(content, encoding='utf-8')
    
    def read_plan(self) -> Optional[str]:
        """Read PLAN.md file."""
        if self.plan_file.exists():
            return self.plan_file.read_text(encoding='utf-8')
        return None
    
    def write_plan(self, content: str) -> None:
        """Write PLAN.md file."""
        self.plan_file.write_text(content, encoding='utf-8')
    
    def read_summary(self) -> Optional[str]:
        """Read SUMMARY.md file."""
        if self.summary_file.exists():
            return self.summary_file.read_text(encoding='utf-8')
        return None
    
    def append_summary(self, content: str) -> None:
        """Append to SUMMARY.md file."""
        timestamp = datetime.now().isoformat()
        entry = f"\n## {timestamp}\n\n{content}\n"
        if self.summary_file.exists():
            existing = self.summary_file.read_text(encoding='utf-8')
            self.summary_file.write_text(existing + entry, encoding='utf-8')
        else:
            self.summary_file.write_text(f"# Summary\n{entry}", encoding='utf-8')
    
    def read_issues(self) -> Optional[str]:
        """Read ISSUES.md file."""
        if self.issues_file.exists():
            return self.issues_file.read_text(encoding='utf-8')
        return None
    
    def write_issues(self, content: str) -> None:
        """Write ISSUES.md file."""
        self.issues_file.write_text(content, encoding='utf-8')
    
    def list_todos(self) -> List[Path]:
        """List all todo files."""
        return list(self.todos_dir.glob("*.md"))
    
    def read_todo(self, todo_name: str) -> Optional[str]:
        """Read a todo file."""
        todo_file = self.todos_dir / f"{todo_name}.md"
        if todo_file.exists():
            return todo_file.read_text(encoding='utf-8')
        return None
    
    def write_todo(self, todo_name: str, content: str) -> None:
        """Write a todo file."""
        todo_file = self.todos_dir / f"{todo_name}.md"
        todo_file.write_text(content, encoding='utf-8')
    
    def delete_todo(self, todo_name: str) -> bool:
        """Delete a todo file."""
        todo_file = self.todos_dir / f"{todo_name}.md"
        if todo_file.exists():
            todo_file.unlink()
            return True
        return False
    
    def read_progress(self, phase_number: int) -> Optional[Dict[str, Any]]:
        """Read progress for a specific phase.
        
        Args:
            phase_number: Phase number to read progress for
            
        Returns:
            Progress dictionary or None if not found
        """
        if not self.progress_file.exists():
            return None
        
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                all_progress = json.load(f)
                phase_key = str(phase_number)
                return all_progress.get(phase_key)
        except (json.JSONDecodeError, KeyError, Exception):
            return None
    
    def write_progress(self, phase_number: int, progress: Dict[str, Any]) -> None:
        """Write progress for a specific phase.
        
        Args:
            phase_number: Phase number
            progress: Progress dictionary to save
        """
        # Read existing progress
        all_progress = {}
        if self.progress_file.exists():
            try:
                with open(self.progress_file, 'r', encoding='utf-8') as f:
                    all_progress = json.load(f)
            except (json.JSONDecodeError, Exception):
                all_progress = {}
        
        # Update progress for this phase
        phase_key = str(phase_number)
        all_progress[phase_key] = progress
        
        # Write back
        with open(self.progress_file, 'w', encoding='utf-8') as f:
            json.dump(all_progress, f, indent=2, ensure_ascii=False)
    
    def get_all_progress(self) -> Dict[str, Dict[str, Any]]:
        """Get all progress data.
        
        Returns:
            Dictionary mapping phase numbers (as strings) to progress data
        """
        if not self.progress_file.exists():
            return {}
        
        try:
            with open(self.progress_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, Exception):
            return {}