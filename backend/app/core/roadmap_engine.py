"""Roadmap generation engine."""

from pathlib import Path
from typing import Optional
from .ollama_client import OllamaClient
from .file_manager import FileManager
from ..utils.prompts import ROADMAP_PROMPT


class RoadmapEngine:
    """Generates roadmaps from project descriptions."""
    
    def __init__(self, ollama_client: OllamaClient):
        """Initialize roadmap engine.
        
        Args:
            ollama_client: Ollama client instance
        """
        self.ollama_client = ollama_client
    
    def generate_roadmap(
        self,
        project_path: Path,
        model: Optional[str] = None
    ) -> str:
        """Generate roadmap for a project.
        
        Args:
            project_path: Path to project directory
            model: Ollama model to use (optional)
            
        Returns:
            Generated roadmap content as Markdown
        """
        file_manager = FileManager(project_path)
        
        # Read PROJECT.md
        project_content = file_manager.read_project()
        if not project_content:
            raise ValueError("PROJECT.md not found. Create project first.")
        
        # Build prompt
        prompt = f"{ROADMAP_PROMPT}\n\n## PROJECT.md\n\n{project_content}\n\nGenerate the ROADMAP.md:"
        
        # Generate roadmap
        result = self.ollama_client.generate(
            prompt=prompt,
            model=model,
            system_prompt="You are an expert project planner. Generate clear, actionable roadmaps."
        )
        
        roadmap_content = result['response']
        
        # Save roadmap
        file_manager.write_roadmap(roadmap_content)
        
        return roadmap_content
