"""Codebase mapping engine for brownfield projects."""

from pathlib import Path
from typing import Optional, Dict, Any, List
from .ollama_client import OllamaClient
from .file_manager import FileManager
from ..utils.prompts import CODEBASE_MAP_PROMPT


class CodebaseMapper:
    """Analyzes existing codebases for brownfield projects."""
    
    def __init__(self, ollama_client: OllamaClient):
        """Initialize codebase mapper.
        
        Args:
            ollama_client: Ollama client instance
        """
        self.ollama_client = ollama_client
    
    async def map_codebase(
        self,
        project_path: Path,
        model: Optional[str] = None,
        max_files: int = 50
    ) -> Dict[str, str]:
        """Map and analyze an existing codebase.
        
        Args:
            project_path: Path to project directory
            model: Ollama model to use (optional)
            max_files: Maximum number of files to analyze
            
        Returns:
            Dictionary mapping document names to content
        """
        # Collect codebase files
        codebase_files = self._collect_codebase_files(project_path, max_files)
        
        # Build codebase context
        codebase_context = self._build_codebase_context(codebase_files)
        
        # Generate documentation for each section
        documents = {}
        sections = [
            'STACK.md',
            'ARCHITECTURE.md',
            'STRUCTURE.md',
            'CONVENTIONS.md',
            'TESTING.md',
            'INTEGRATIONS.md',
            'CONCERNS.md'
        ]
        
        for section in sections:
            prompt = f"{CODEBASE_MAP_PROMPT}\n\n## Codebase Context\n\n{codebase_context}\n\nGenerate {section}:"
            
            result = await self.ollama_client.generate(
                prompt=prompt,
                model=model,
                system_prompt="You are an expert codebase analyst. Provide detailed, accurate analysis."
            )
            
            documents[section] = result['response']
        
        # Save documents to .planning/codebase/
        codebase_dir = FileManager(project_path).planning_dir / "codebase"
        codebase_dir.mkdir(exist_ok=True)
        
        for doc_name, content in documents.items():
            doc_path = codebase_dir / doc_name
            doc_path.write_text(content, encoding='utf-8')
        
        return documents
    
    def _collect_codebase_files(self, project_path: Path, max_files: int) -> List[Path]:
        """Collect codebase files for analysis.
        
        Args:
            project_path: Path to project directory
            max_files: Maximum number of files to collect
            
        Returns:
            List of file paths
        """
        files = []
        exclude_dirs = {'.git', '.planning', 'node_modules', '__pycache__', '.venv', 'venv', 'dist', 'build'}
        
        for path in project_path.rglob('*'):
            if path.is_file():
                # Skip excluded directories
                if any(excluded in path.parts for excluded in exclude_dirs):
                    continue
                
                # Only include code files
                if path.suffix in {'.py', '.ts', '.tsx', '.js', '.jsx', '.json', '.md', '.yaml', '.yml', '.toml'}:
                    files.append(path)
                    if len(files) >= max_files:
                        break
        
        return files
    
    def _build_codebase_context(self, files: List[Path]) -> str:
        """Build codebase context string from files.
        
        Args:
            files: List of file paths
            
        Returns:
            Context string
        """
        context_parts = []
        
        for file_path in files[:20]:  # Limit to first 20 files for context
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                # Truncate very long files
                if len(content) > 2000:
                    content = content[:2000] + "\n... (truncated)"
                
                context_parts.append(f"## {file_path.name}\n```\n{content}\n```\n")
            except Exception:
                continue
        
        return "\n".join(context_parts)
