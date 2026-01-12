"""Task execution engine."""

from pathlib import Path
from typing import Optional, Dict, Any, List, Callable
from .ollama_client import OllamaClient
from .file_manager import FileManager
from ..utils.prompts import TASK_EXECUTE_PROMPT
from ..utils.xml_parser import TaskParser


class TaskExecutor:
    """Executes tasks using Ollama subagents."""
    
    def __init__(self, ollama_client: OllamaClient):
        """Initialize task executor.
        
        Args:
            ollama_client: Ollama client instance
        """
        self.ollama_client = ollama_client
        self.progress_callback: Optional[Callable[[Dict[str, Any]], None]] = None
    
    async def execute_task(
        self,
        project_path: Path,
        task: Dict[str, Any],
        model: Optional[str] = None
    ) -> Dict[str, Any]:
        """Execute a single task.
        
        Args:
            project_path: Path to project directory
            task: Task dictionary with name, action, etc.
            model: Ollama model to use (optional)
            
        Returns:
            Execution result dictionary
        """
        # Convert task to XML
        task_xml = TaskParser.task_to_xml(task)
        
        # Build prompt
        prompt = TASK_EXECUTE_PROMPT.format(task_xml=task_xml)
        
        # Notify progress
        if self.progress_callback:
            self.progress_callback({
                'status': 'running',
                'task': task.get('name', 'Unknown'),
                'message': 'Executing task...'
            })
        
        # Execute task
        result = await self.ollama_client.generate(
            prompt=prompt,
            model=model,
            system_prompt="You are an expert software developer. Implement tasks accurately and completely."
        )
        
        execution_result = {
            'task_id': task.get('id', 'unknown'),
            'task_name': task.get('name', 'Unknown'),
            'status': 'complete',
            'result': result['response'],
            'tokens': result.get('tokens', {})
        }
        
        # Notify completion
        if self.progress_callback:
            self.progress_callback({
                'status': 'complete',
                'task': task.get('name', 'Unknown'),
                'message': 'Task completed'
            })
        
        # Append to summary
        file_manager = FileManager(project_path)
        summary_content = f"## Task: {task.get('name', 'Unknown')}\n\n{result['response']}\n"
        file_manager.append_summary(summary_content)
        
        return execution_result
    
    async def execute_phase(
        self,
        project_path: Path,
        phase_number: int,
        tasks: List[Dict[str, Any]],
        model: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Execute all tasks in a phase.
        
        Args:
            project_path: Path to project directory
            phase_number: Phase number
            tasks: List of task dictionaries
            model: Ollama model to use (optional)
            
        Returns:
            List of execution results
        """
        results = []
        
        for i, task in enumerate(tasks):
            try:
                result = await self.execute_task(project_path, task, model)
                results.append(result)
            except Exception as e:
                # Task failed
                results.append({
                    'task_id': task.get('id', 'unknown'),
                    'task_name': task.get('name', 'Unknown'),
                    'status': 'failed',
                    'error': str(e)
                })
                if self.progress_callback:
                    self.progress_callback({
                        'status': 'error',
                        'task': task.get('name', 'Unknown'),
                        'message': f'Task failed: {str(e)}'
                    })
        
        return results
    
    def set_progress_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Set progress callback function.
        
        Args:
            callback: Function to call with progress updates
        """
        self.progress_callback = callback
