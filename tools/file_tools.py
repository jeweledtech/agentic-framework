"""
File Tools for Agents

Simple file read/write tools for agent use.
These demonstrate how to create tools that interact with the file system.
"""

import os
from pathlib import Path
from typing import Optional


class FileReadTool:
    """Tool for reading files"""
    
    name = "file_read"
    description = "Read the contents of a file"
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize with optional base path for security
        
        Args:
            base_path: Base directory to restrict file access
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
    
    def run(self, file_path: str) -> str:
        """
        Read a file and return its contents
        
        Args:
            file_path: Path to the file to read
            
        Returns:
            File contents as string
        """
        try:
            # Resolve path and ensure it's within base_path for security
            full_path = (self.base_path / file_path).resolve()
            
            # Security check: ensure path is within base_path
            if not str(full_path).startswith(str(self.base_path)):
                return f"Error: Access denied. File must be within {self.base_path}"
            
            if not full_path.exists():
                return f"Error: File not found: {file_path}"
            
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return content
        except Exception as e:
            return f"Error reading file: {str(e)}"
    
    def __call__(self, file_path: str) -> str:
        """Make the tool callable for CrewAI compatibility"""
        return self.run(file_path)


class FileWriteTool:
    """Tool for writing files"""
    
    name = "file_write"
    description = "Write content to a file"
    
    def __init__(self, base_path: Optional[str] = None):
        """
        Initialize with optional base path for security
        
        Args:
            base_path: Base directory to restrict file access
        """
        self.base_path = Path(base_path) if base_path else Path.cwd()
    
    def run(self, file_path: str, content: str, append: bool = False) -> str:
        """
        Write content to a file
        
        Args:
            file_path: Path to the file to write
            content: Content to write
            append: Whether to append or overwrite
            
        Returns:
            Success or error message
        """
        try:
            # Resolve path and ensure it's within base_path for security
            full_path = (self.base_path / file_path).resolve()
            
            # Security check: ensure path is within base_path
            if not str(full_path).startswith(str(self.base_path)):
                return f"Error: Access denied. File must be within {self.base_path}"
            
            # Create parent directories if they don't exist
            full_path.parent.mkdir(parents=True, exist_ok=True)
            
            mode = 'a' if append else 'w'
            with open(full_path, mode, encoding='utf-8') as f:
                f.write(content)
            
            action = "appended to" if append else "written to"
            return f"Successfully {action} file: {file_path}"
        except Exception as e:
            return f"Error writing file: {str(e)}"
    
    def __call__(self, file_path: str, content: str) -> str:
        """Make the tool callable for CrewAI compatibility"""
        return self.run(file_path, content)