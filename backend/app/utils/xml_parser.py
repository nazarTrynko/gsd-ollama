"""XML task parser for GSD Ollama."""

import re
from typing import List, Dict, Any, Optional
from xml.etree import ElementTree as ET


class TaskParser:
    """Parser for XML-formatted task plans."""
    
    @staticmethod
    def parse_task_xml(xml_content: str) -> List[Dict[str, Any]]:
        """Parse XML task plan into list of task dictionaries.
        
        Args:
            xml_content: XML string containing task definitions
            
        Returns:
            List of task dictionaries with keys: name, type, files, action, verify, done
        """
        tasks = []
        
        # Try to parse as XML
        try:
            # Wrap in root element if needed
            if not xml_content.strip().startswith('<'):
                return []
            
            # Try to find task elements
            root = ET.fromstring(f"<root>{xml_content}</root>")
            
            for task_elem in root.findall('.//task'):
                task = {
                    'type': task_elem.get('type', 'auto'),
                    'name': '',
                    'files': [],
                    'action': '',
                    'verify': '',
                    'done': ''
                }
                
                # Extract name
                name_elem = task_elem.find('name')
                if name_elem is not None:
                    task['name'] = name_elem.text or ''
                
                # Extract files
                files_elem = task_elem.find('files')
                if files_elem is not None:
                    files_text = files_elem.text or ''
                    task['files'] = [f.strip() for f in files_text.split(',') if f.strip()]
                
                # Extract action
                action_elem = task_elem.find('action')
                if action_elem is not None:
                    task['action'] = action_elem.text or ''
                
                # Extract verify
                verify_elem = task_elem.find('verify')
                if verify_elem is not None:
                    task['verify'] = verify_elem.text or ''
                
                # Extract done
                done_elem = task_elem.find('done')
                if done_elem is not None:
                    task['done'] = done_elem.text or ''
                
                if task['name']:  # Only add if has a name
                    tasks.append(task)
        
        except ET.ParseError:
            # Fallback to regex parsing if XML parsing fails
            tasks = TaskParser._parse_with_regex(xml_content)
        
        return tasks
    
    @staticmethod
    def _parse_with_regex(xml_content: str) -> List[Dict[str, Any]]:
        """Fallback regex-based parser for task XML.
        
        Args:
            xml_content: XML string containing task definitions
            
        Returns:
            List of task dictionaries
        """
        tasks = []
        
        # Pattern to match task blocks
        task_pattern = r'<task[^>]*>(.*?)</task>'
        matches = re.finditer(task_pattern, xml_content, re.DOTALL)
        
        for match in matches:
            task_content = match.group(1)
            task = {
                'type': 'auto',
                'name': '',
                'files': [],
                'action': '',
                'verify': '',
                'done': ''
            }
            
            # Extract type from opening tag
            type_match = re.search(r'<task\s+type="([^"]+)"', match.group(0))
            if type_match:
                task['type'] = type_match.group(1)
            
            # Extract name
            name_match = re.search(r'<name>(.*?)</name>', task_content, re.DOTALL)
            if name_match:
                task['name'] = name_match.group(1).strip()
            
            # Extract files
            files_match = re.search(r'<files>(.*?)</files>', task_content, re.DOTALL)
            if files_match:
                files_text = files_match.group(1).strip()
                task['files'] = [f.strip() for f in files_text.split(',') if f.strip()]
            
            # Extract action
            action_match = re.search(r'<action>(.*?)</action>', task_content, re.DOTALL)
            if action_match:
                task['action'] = action_match.group(1).strip()
            
            # Extract verify
            verify_match = re.search(r'<verify>(.*?)</verify>', task_content, re.DOTALL)
            if verify_match:
                task['verify'] = verify_match.group(1).strip()
            
            # Extract done
            done_match = re.search(r'<done>(.*?)</done>', task_content, re.DOTALL)
            if done_match:
                task['done'] = done_match.group(1).strip()
            
            if task['name']:
                tasks.append(task)
        
        return tasks
    
    @staticmethod
    def task_to_xml(task: Dict[str, Any]) -> str:
        """Convert a task dictionary to XML format.
        
        Args:
            task: Task dictionary with keys: name, type, files, action, verify, done
            
        Returns:
            XML string representation of the task
        """
        task_type = task.get('type', 'auto')
        name = task.get('name', '')
        files = task.get('files', [])
        action = task.get('action', '')
        verify = task.get('verify', '')
        done = task.get('done', '')
        
        xml = f'<task type="{task_type}">\n'
        xml += f'  <name>{name}</name>\n'
        
        if files:
            xml += f'  <files>{", ".join(files)}</files>\n'
        
        if action:
            xml += f'  <action>\n{action}\n  </action>\n'
        
        if verify:
            xml += f'  <verify>{verify}</verify>\n'
        
        if done:
            xml += f'  <done>{done}</done>\n'
        
        xml += '</task>'
        return xml
