"""Project manager for GSD Ollama."""

from pathlib import Path
from typing import Optional, Dict, Any
from .file_manager import FileManager


class ProjectManager:
    """Manages project state and .planning/ directory."""
    
    def __init__(self, project_path: Path):
        """Initialize project manager.
        
        Args:
            project_path: Path to the project root directory
        """
        self.project_path = Path(project_path)
        self.file_manager = FileManager(self.project_path)
    
    def get_project_info(self) -> Dict[str, Any]:
        """Get project information from PROJECT.md."""
        project_content = self.file_manager.read_project()
        if not project_content:
            return {
                "exists": False,
                "name": None,
                "description": None
            }
        
        # Parse basic info from PROJECT.md
        # Simple parsing - assumes standard format
        lines = project_content.split('\n')
        name = None
        description_lines = []
        
        for i, line in enumerate(lines):
            if line.startswith('# '):
                name = line[2:].strip()
            elif line.startswith('## Description') or line.startswith('## Overview'):
                # Get description from next lines
                for j in range(i + 1, len(lines)):
                    if lines[j].startswith('#'):
                        break
                    if lines[j].strip():
                        description_lines.append(lines[j].strip())
        
        return {
            "exists": True,
            "name": name or "Untitled Project",
            "description": '\n'.join(description_lines) if description_lines else None,
            "path": str(self.project_path)
        }
    
    def get_roadmap(self) -> Optional[str]:
        """Get roadmap content."""
        return self.file_manager.read_roadmap()
    
    def get_state(self) -> Optional[str]:
        """Get state content."""
        return self.file_manager.read_state()
    
    def get_plan(self) -> Optional[str]:
        """Get current plan."""
        return self.file_manager.read_plan()
    
    def get_summary(self) -> Optional[str]:
        """Get summary content."""
        return self.file_manager.read_summary()
    
    def get_issues(self) -> Optional[str]:
        """Get issues content."""
        return self.file_manager.read_issues()
    
    def update_state(self, updates: Dict[str, Any]) -> None:
        """Update STATE.md with new information."""
        state_content = self.file_manager.read_state() or "# State\n\n"
        
        # Simple state update - append new information
        timestamp = Path(__file__).stat().st_mtime  # Use file modification time as proxy
        new_section = f"\n## Update\n\n"
        for key, value in updates.items():
            new_section += f"- **{key}**: {value}\n"
        new_section += "\n"
        
        self.file_manager.write_state(state_content + new_section)
