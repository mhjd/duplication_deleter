"""
Duplicate file detector module.
Handles file size comparison and MD5 hashing for duplicate detection.
"""

import os
import hashlib
from typing import Dict, List, Set, Optional, Callable
from pathlib import Path
import threading
import time


class DuplicateDetector:
    """
    Detects duplicate files using file size comparison and MD5 hashing.
    """
    
    def __init__(self, progress_callback: Optional[Callable] = None):
        self.progress_callback = progress_callback
        self.stop_search = False
        self.current_operation = ""
        
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
        
    def calculate_md5(self, file_path: str) -> Optional[str]:
        """
        Calculate MD5 hash of a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            MD5 hash string or None if file cannot be read
        """
        try:
            # Normalize path first
            normalized_path = self._normalize_path(file_path)
            
            hash_md5 = hashlib.md5()
            with open(normalized_path, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hash_md5.update(chunk)
            return hash_md5.hexdigest()
        except (IOError, OSError, PermissionError):
            # File is inaccessible or in use
            return None
    
    def get_file_size(self, file_path: str) -> Optional[int]:
        """
        Get file size in bytes.
        
        Args:
            file_path: Path to the file
            
        Returns:
            File size in bytes or None if file cannot be accessed
        """
        try:
            # Normalize path first
            normalized_path = self._normalize_path(file_path)
            return os.path.getsize(normalized_path)
        except (IOError, OSError, PermissionError):
            return None
    
    def is_hidden_file(self, file_path: str) -> bool:
        """
        Check if a file is hidden (starts with '.').
        
        Args:
            file_path: Path to the file
            
        Returns:
            True if file is hidden, False otherwise
        """
        return os.path.basename(file_path).startswith('.')
    
    def get_all_files(self, root_dir: str) -> List[str]:
        """
        Recursively get all files in a directory, excluding hidden files.
        
        Args:
            root_dir: Root directory to search
            
        Returns:
            List of file paths
        """
        files = []
        total_dirs = 0
        processed_dirs = 0
        
        # Normalize root directory first
        normalized_root = self._normalize_path(root_dir)
        
        # Count total directories for progress
        for root, dirs, _ in os.walk(normalized_root):
            total_dirs += 1
        
        for root, dirs, filenames in os.walk(normalized_root):
            if self.stop_search:
                break
                
            processed_dirs += 1
            
            # Update progress
            if self.progress_callback:
                progress = (processed_dirs / total_dirs) * 30  # 30% for file discovery
                self.progress_callback(progress, f"Scanning directory: {root}")
            
            for filename in filenames:
                if self.stop_search:
                    break
                    
                file_path = os.path.join(root, filename)
                
                # Normalize the file path
                normalized_file_path = self._normalize_path(file_path)
                
                # Skip hidden files
                if self.is_hidden_file(normalized_file_path):
                    continue
                
                # Skip if file is not accessible
                if not os.path.isfile(normalized_file_path):
                    continue
                
                files.append(normalized_file_path)
        
        return files
    
    def group_by_size(self, files: List[str]) -> Dict[int, List[str]]:
        """
        Group files by their size.
        
        Args:
            files: List of file paths
            
        Returns:
            Dictionary mapping file size to list of files with that size
        """
        size_groups = {}
        total_files = len(files)
        
        for i, file_path in enumerate(files):
            if self.stop_search:
                break
                
            # Update progress
            if self.progress_callback:
                progress = 30 + (i / total_files) * 30  # 30-60% for size grouping
                self.progress_callback(progress, f"Analyzing file sizes: {os.path.basename(file_path)}")
            
            file_size = self.get_file_size(file_path)
            if file_size is not None:
                if file_size not in size_groups:
                    size_groups[file_size] = []
                size_groups[file_size].append(file_path)
        
        # Only keep groups with multiple files
        return {size: files for size, files in size_groups.items() if len(files) > 1}
    
    def find_duplicates_by_hash(self, size_groups: Dict[int, List[str]]) -> Dict[str, List[str]]:
        """
        Find duplicates by calculating MD5 hashes for files with the same size.
        
        Args:
            size_groups: Dictionary mapping file size to list of files
            
        Returns:
            Dictionary mapping MD5 hash to list of duplicate files
        """
        duplicates = {}
        total_files = sum(len(files) for files in size_groups.values())
        processed_files = 0
        
        for size, files in size_groups.items():
            if self.stop_search:
                break
                
            for file_path in files:
                if self.stop_search:
                    break
                    
                processed_files += 1
                
                # Update progress
                if self.progress_callback:
                    progress = 60 + (processed_files / total_files) * 40  # 60-100% for hashing
                    self.progress_callback(progress, f"Calculating hash: {os.path.basename(file_path)}")
                
                file_hash = self.calculate_md5(file_path)
                if file_hash is not None:
                    if file_hash not in duplicates:
                        duplicates[file_hash] = []
                    duplicates[file_hash].append(file_path)
        
        # Only keep groups with multiple files (actual duplicates)
        return {hash_val: files for hash_val, files in duplicates.items() if len(files) > 1}
    
    def find_duplicates(self, root_dir: str) -> Dict[str, List[str]]:
        """
        Find all duplicate files in a directory.
        
        Args:
            root_dir: Root directory to search
            
        Returns:
            Dictionary mapping hash to list of duplicate files
        """
        self.stop_search = False
        
        if self.progress_callback:
            self.progress_callback(0, "Starting duplicate search...")
        
        # Step 1: Get all files
        files = self.get_all_files(root_dir)
        
        if self.stop_search:
            return {}
        
        # Step 2: Group by size
        size_groups = self.group_by_size(files)
        
        if self.stop_search:
            return {}
        
        # Step 3: Find duplicates by hash
        duplicates = self.find_duplicates_by_hash(size_groups)
        
        if self.progress_callback:
            self.progress_callback(100, f"Found {len(duplicates)} duplicate groups")
        
        return duplicates
    
    def stop(self):
        """Stop the current search operation."""
        self.stop_search = True 