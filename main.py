#!/usr/bin/env python3
"""
Main entry point for the Duplicate File Deleter application.
Run this file to start the application.
"""

import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.main_ui import main

if __name__ == "__main__":
    main() 