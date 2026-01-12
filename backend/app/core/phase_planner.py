"""Phase planning engine."""

import uuid
from pathlib import Path
from typing import Optional, List, Dict, Any
from .ollama_client import OllamaClient
from .file_manager import FileManager
from ..utils.prompts import PHASE_PLAN_PROMPT
from ..utils.xml_parser import TaskParser


class PhasePlanner:
    """Creates XML-formatted task plans for phases."""
    
    def __init__(self, ollama_client: OllamaClient):
        """Initialize phase planner.
        
        Args:
            ollama_client: Ollama client instance
        """
        self.ollama_client = ollama_client
    
    async def plan_phase(
        self,
        project_path: Path,
        phase_number: int,
        model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Plan tasks for a specific phase.
        
        Args:
            project_path: Path to project directory
            phase_number: Phase number to plan
            model: Ollama model to use (optional)
            
        Returns:
            List of task dictionaries
        """
        file_manager = FileManager(project_path)
        
        # Read ROADMAP.md
        roadmap_content = file_manager.read_roadmap()
        if not roadmap_content:
            raise ValueError("ROADMAP.md not found. Create roadmap first.")
        
        # Extract phase description from roadmap
        phase_description = self._extract_phase_description(roadmap_content, phase_number)
        if not phase_description:
            raise ValueError(f"Phase {phase_number} not found in roadmap")
        
        # Build prompt
        prompt = f"{PHASE_PLAN_PROMPT}\n\n## Phase {phase_number}\n\n{phase_description}\n\nGenerate the task plan:"
        
        # Generate task plan
        result = await self.ollama_client.generate(
            prompt=prompt,
            model=model,
            system_prompt="You are an expert task planner. Create atomic, actionable tasks."
        )
        
        task_xml = result['response']
        
        # Parse XML tasks
        tasks = TaskParser.parse_task_xml(task_xml)
        
        # Add IDs to tasks with UUID for uniqueness
        for i, task in enumerate(tasks):
            task['id'] = f"task-{phase_number}-{i+1}-{uuid.uuid4().hex[:8]}"
        
        # Save plan
        plan_content = f"# Phase {phase_number} Plan\n\n{task_xml}\n"
        file_manager.write_plan(plan_content)
        
        return tasks
    
    def _extract_phase_description(self, roadmap_content: str, phase_number: int) -> Optional[str]:
        """Extract phase description from roadmap.
        
        Args:
            roadmap_content: Roadmap markdown content
            phase_number: Phase number to extract
            
        Returns:
            Phase description or None if not found
        """
        lines = roadmap_content.split('\n')
        phase_section = []
        in_phase = False
        
        for line in lines:
            # Look for phase header
            if f"Phase {phase_number}:" in line or f"### Phase {phase_number}" in line:
                in_phase = True
                phase_section.append(line)
                continue
            
            if in_phase:
                # Stop at next phase or milestone
                if line.startswith('### Phase') or line.startswith('## Milestone'):
                    break
                phase_section.append(line)
        
        if phase_section:
            return '\n'.join(phase_section)
        return None
