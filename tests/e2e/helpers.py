"""Test utilities and helpers for e2e tests."""

import subprocess
import time
import signal
import os
from pathlib import Path
from typing import Optional, Dict, Any
import requests


class ServerManager:
    """Manages backend and frontend server processes for e2e tests."""
    
    def __init__(self, backend_port: int = 8000, frontend_port: int = 5173):
        self.backend_port = backend_port
        self.frontend_port = frontend_port
        self.backend_process: Optional[subprocess.Popen] = None
        self.frontend_process: Optional[subprocess.Popen] = None
        self.backend_url = f"http://localhost:{backend_port}"
        self.frontend_url = f"http://localhost:{frontend_port}"
    
    def start_backend(self, backend_dir: Path) -> None:
        """Start backend server."""
        if self.backend_process:
            return
        
        env = os.environ.copy()
        env['PYTHONPATH'] = str(backend_dir.parent)
        
        self.backend_process = subprocess.Popen(
            ['python', '-m', 'uvicorn', 'app.main:app', '--port', str(self.backend_port)],
            cwd=backend_dir,
            env=env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        # Wait for server to be ready
        self._wait_for_server(self.backend_url, timeout=30)
    
    def start_frontend(self, frontend_dir: Path) -> None:
        """Start frontend dev server."""
        if self.frontend_process:
            return
        
        self.frontend_process = subprocess.Popen(
            ['npm', 'run', 'dev'],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        
        # Wait for server to be ready
        self._wait_for_server(self.frontend_url, timeout=60)
    
    def _wait_for_server(self, url: str, timeout: int = 30) -> None:
        """Wait for server to be ready."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get(url, timeout=2)
                if response.status_code in [200, 404]:  # 404 is OK, means server is up
                    return
            except requests.RequestException:
                pass
            time.sleep(0.5)
        
        raise TimeoutError(f"Server at {url} did not become ready in {timeout} seconds")
    
    def stop_backend(self) -> None:
        """Stop backend server."""
        if self.backend_process:
            self.backend_process.terminate()
            try:
                self.backend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.backend_process.kill()
            self.backend_process = None
    
    def stop_frontend(self) -> None:
        """Stop frontend server."""
        if self.frontend_process:
            self.frontend_process.terminate()
            try:
                self.frontend_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.frontend_process.kill()
            self.frontend_process = None
    
    def stop_all(self) -> None:
        """Stop all servers."""
        self.stop_backend()
        self.stop_frontend()


def create_test_project_data(name: str = "E2E Test Project") -> Dict[str, Any]:
    """Create test project data."""
    return {
        "name": name,
        "description": f"Test project for e2e testing: {name}",
        "initial_task": "Set up e2e testing infrastructure"
    }


def wait_for_api_ready(url: str, timeout: int = 30) -> bool:
    """Wait for API to be ready."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            response = requests.get(f"{url}/health", timeout=2)
            if response.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(0.5)
    return False
