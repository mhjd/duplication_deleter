"""
File manager module for handling file operations including moving files to trash.
"""

import os
import shutil
from typing import List, Dict, Optional
from pathlib import Path
import send2trash


class FileManager:
    """
    Handles file operations including moving files to trash.
    """
    
    def __init__(self):
        self.deleted_files = []
        self.errors = []
    
    def _normalize_path(self, file_path: str) -> str:
        """
        Normalize file path for the current operating system.
        
        Args:
            file_path: Path to normalize
            
        Returns:
            Normalized path string
        """
        # Convert to Path object and resolve
        path = Path(file_path)
        try:
            # Resolve path to absolute path and normalize separators
            normalized = path.resolve()
            return str(normalized)
        except (OSError, ValueError):
            # If resolve fails, try basic normalization
            return os.path.normpath(os.path.abspath(file_path))
    
    def move_to_trash(self, file_path: str) -> bool:
        """
        Move a file to trash (system trash/recycle bin).
        
        Args:
            file_path: Path to the file to be moved to trash
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Normalize the path first
            normalized_path = self._normalize_path(file_path)
            
            # Check if file exists using normalized path
            if not os.path.exists(normalized_path):
                self.errors.append(f"File not found: {normalized_path}")
                return False
            
            # Check if file is actually a file (not a directory)
            if not os.path.isfile(normalized_path):
                self.errors.append(f"Path is not a file: {normalized_path}")
                return False
            
            # Try to move to trash
            send2trash.send2trash(normalized_path)
            self.deleted_files.append(normalized_path)
            return True
            
        except PermissionError as e:
            self.errors.append(f"Permission denied for {file_path}: {str(e)}")
            return False
        except FileNotFoundError as e:
            self.errors.append(f"File not found {file_path}: {str(e)}")
            return False
        except OSError as e:
            self.errors.append(f"OS error moving {file_path} to trash: {str(e)}")
            return False
        except Exception as e:
            self.errors.append(f"Error moving {file_path} to trash: {str(e)}")
            return False
    
    def move_files_to_trash(self, file_paths: List[str]) -> Dict[str, bool]:
        """
        Move multiple files to trash.
        
        Args:
            file_paths: List of file paths to be moved to trash
            
        Returns:
            Dictionary mapping file path to success status
        """
        results = {}
        for file_path in file_paths:
            results[file_path] = self.move_to_trash(file_path)
        return results
    
    def get_file_info(self, file_path: str) -> Optional[Dict]:
        """
        Get file information including size, modification time, etc.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Dictionary with file information or None if file doesn't exist
        """
        try:
            # Normalize path first
            normalized_path = self._normalize_path(file_path)
            
            if not os.path.exists(normalized_path):
                return None
                
            stat_info = os.stat(normalized_path)
            return {
                'path': normalized_path,
                'name': os.path.basename(normalized_path),
                'size': stat_info.st_size,
                'modified': stat_info.st_mtime,
                'directory': os.path.dirname(normalized_path),
                'exists': True
            }
        except Exception as e:
            return None
    
    def format_file_size(self, size_bytes: int) -> str:
        """
        Format file size in human-readable format.
        
        Args:
            size_bytes: Size in bytes
            
        Returns:
            Formatted size string
        """
        if size_bytes == 0:
            return "0 B"
        
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        size_float = float(size_bytes)
        while size_float >= 1024 and i < len(size_names) - 1:
            size_float /= 1024.0
            i += 1
        
        return f"{size_float:.1f} {size_names[i]}"
    
    def get_relative_path(self, file_path: str, base_path: str) -> str:
        """
        Get relative path from base path.
        
        Args:
            file_path: Full file path
            base_path: Base directory path
            
        Returns:
            Relative path string
        """
        try:
            # Normalize both paths first
            normalized_file = self._normalize_path(file_path)
            normalized_base = self._normalize_path(base_path)
            return os.path.relpath(normalized_file, normalized_base)
        except ValueError:
            return file_path
    
    def clear_errors(self):
        """Clear the error list."""
        self.errors = []
    
    def clear_deleted_files(self):
        """Clear the deleted files list."""
        self.deleted_files = []
    
    def get_errors(self) -> List[str]:
        """Get list of errors."""
        return self.errors.copy()
    
    def get_deleted_files(self) -> List[str]:
        """Get list of deleted files."""
        return self.deleted_files.copy() 