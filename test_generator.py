#!/usr/bin/env python3
"""
Test generator script for the Duplicate File Deleter.
Creates a test folder with duplicate files to test the application.
"""

import os
import shutil
import random
import string
from pathlib import Path


def generate_random_content(size: int) -> str:
    """Generate random content of specified size."""
    return ''.join(random.choices(string.ascii_letters + string.digits + ' \n', k=size))


def create_test_structure():
    """Create test directory structure with duplicate files."""
    
    # Test folder path
    test_folder = Path("test_duplicates")
    
    # Remove existing test folder if it exists
    if test_folder.exists():
        shutil.rmtree(test_folder)
    
    # Create main test folder
    test_folder.mkdir()
    
    # Create subfolders
    subfolders = [
        "documents",
        "documents/work",
        "documents/personal",
        "images",
        "images/photos",
        "images/screenshots",
        "downloads",
        "downloads/software",
        "misc",
        "misc/temp"
    ]
    
    for subfolder in subfolders:
        (test_folder / subfolder).mkdir(parents=True, exist_ok=True)
    
    # Define test files with their content
    test_files = [
        # Text files
        {
            "name": "document1.txt",
            "content": "This is a test document with some content.\nLine 2 of the document.\nLine 3 of the document.",
            "locations": ["documents/", "documents/work/", "downloads/"]
        },
        {
            "name": "readme.txt",
            "content": "README\n======\n\nThis is a readme file with important information.\nPlease read carefully before proceeding.",
            "locations": ["", "documents/", "misc/"]
        },
        {
            "name": "notes.txt",
            "content": "Meeting Notes\n=============\n\n1. Project deadline: Next Friday\n2. Team meeting: Monday 10 AM\n3. Code review: Wednesday",
            "locations": ["documents/work/", "documents/personal/"]
        },
        
        # Image files (simulated binary content)
        {
            "name": "image1.jpg",
            "content": b'\xff\xd8\xff\xe0\x00\x10JFIF\x00\x01\x01\x01\x00H\x00H\x00\x00' + b'fake_image_data' * 100,
            "locations": ["images/", "images/photos/", "downloads/"],
            "binary": True
        },
        {
            "name": "screenshot.png",
            "content": b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x10\x00\x00\x00\x10' + b'fake_png_data' * 80,
            "locations": ["images/screenshots/", "misc/temp/"],
            "binary": True
        },
        
        # Code files
        {
            "name": "script.py",
            "content": """#!/usr/bin/env python3

def main():
    print("Hello, World!")
    print("This is a test script")
    
    for i in range(10):
        print(f"Number: {i}")

if __name__ == "__main__":
    main()
""",
            "locations": ["downloads/software/", "misc/", "documents/work/"]
        },
        
        # Configuration files
        {
            "name": "config.json",
            "content": """{
    "version": "1.0.0",
    "settings": {
        "debug": true,
        "max_files": 1000,
        "timeout": 30
    },
    "paths": [
        "/usr/local/bin",
        "/usr/bin",
        "/bin"
    ]
}""",
            "locations": ["", "downloads/software/"]
        },
        
        # Data files
        {
            "name": "data.csv",
            "content": """Name,Age,City
John,25,New York
Jane,30,San Francisco
Bob,35,Chicago
Alice,28,Boston
Charlie,32,Seattle""",
            "locations": ["documents/work/", "downloads/"]
        }
    ]
    
    # Create files with duplicates
    for file_info in test_files:
        content = file_info["content"]
        is_binary = file_info.get("binary", False)
        
        for location in file_info["locations"]:
            file_path = test_folder / location / file_info["name"]
            
            # Create unique names for some duplicates
            if location != file_info["locations"][0]:  # Not the first location
                # Sometimes keep the same name, sometimes add suffix
                if random.random() < 0.5:  # 50% chance to add suffix
                    name_parts = file_info["name"].rsplit('.', 1)
                    if len(name_parts) == 2:
                        base_name, ext = name_parts
                        suffixes = ['_copy', '_backup', '_old', '_new', '_final', '(1)', '(2)']
                        suffix = random.choice(suffixes)
                        new_name = f"{base_name}{suffix}.{ext}"
                        file_path = test_folder / location / new_name
            
            # Write file
            mode = 'wb' if is_binary else 'w'
            encoding = None if is_binary else 'utf-8'
            
            with open(file_path, mode, encoding=encoding) as f:
                f.write(content)
    
    # Create some unique files (no duplicates)
    unique_files = [
        {"name": "unique1.txt", "content": "This file has no duplicates.", "location": "documents/"},
        {"name": "unique2.log", "content": "Log file with unique content.\n2023-01-01 10:00:00 INFO: Application started", "location": "misc/"},
        {"name": "unique3.md", "content": "# Unique Markdown File\n\nThis file exists only once.", "location": "documents/personal/"},
    ]
    
    for file_info in unique_files:
        file_path = test_folder / file_info["location"] / file_info["name"]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_info["content"])
    
    # Create some hidden files (should be ignored)
    hidden_files = [
        {"name": ".hidden1.txt", "content": "This is a hidden file.", "location": ""},
        {"name": ".DS_Store", "content": "Mac system file", "location": "images/"},
        {"name": ".gitignore", "content": "*.log\n*.tmp\n", "location": "documents/work/"},
    ]
    
    for file_info in hidden_files:
        file_path = test_folder / file_info["location"] / file_info["name"]
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(file_info["content"])
    
    # Create some empty files
    empty_files = [
        "documents/empty1.txt",
        "documents/empty2.txt",
        "misc/empty3.log"
    ]
    
    for empty_file in empty_files:
        file_path = test_folder / empty_file
        file_path.touch()
    
    print(f"✅ Test structure created successfully in '{test_folder}'")
    print("\nTest structure includes:")
    print("- Multiple duplicate files with same content")
    print("- Files with different names but same content")
    print("- Files in different subdirectories")
    print("- Unique files (no duplicates)")
    print("- Hidden files (should be ignored)")
    print("- Empty files")
    print("- Various file types: text, binary, code, data")
    print("\nYou can now use this folder to test the Duplicate File Deleter application.")


def print_test_summary():
    """Print a summary of the test structure."""
    test_folder = Path("test_duplicates")
    
    if not test_folder.exists():
        print("❌ Test folder does not exist. Run the script first to create it.")
        return
    
    print(f"📁 Test folder: {test_folder.absolute()}")
    print("\nFolder structure:")
    
    total_files = 0
    total_size = 0
    
    for root, dirs, files in os.walk(test_folder):
        level = root.replace(str(test_folder), '').count(os.sep)
        indent = ' ' * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        
        subindent = ' ' * 2 * (level + 1)
        for file in files:
            file_path = os.path.join(root, file)
            file_size = os.path.getsize(file_path)
            total_files += 1
            total_size += file_size
            
            # Mark hidden files
            hidden_mark = " (hidden)" if file.startswith('.') else ""
            print(f"{subindent}{file} ({file_size} bytes){hidden_mark}")
    
    print(f"\n📊 Summary:")
    print(f"Total files: {total_files}")
    print(f"Total size: {total_size:,} bytes")
    print(f"Expected duplicate groups: ~5-7 (excluding hidden files)")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--summary":
        print_test_summary()
    else:
        print("🔧 Creating test structure for Duplicate File Deleter...")
        create_test_structure()
        print("\n" + "="*50)
        print_test_summary() 