# Duplicate File Deleter

## Description

Duplicate file deleter is a cross-platform Python application designed to detect, select, and delete duplicate files in a specified folder and its subfolders.

## Installation

### Requirements
- Python 3.7 or higher
- Windows, macOS, or Linux

### Setup
1. Clone or download this repository
2. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Running the Application
```bash
python3 main.py
```

## Usage

### Basic Workflow
1. **Launch the application** by running `python3 main.py`
2. **Select a folder** to search by clicking "Browse" or typing the path
3. **Start the search** by clicking "Search for Duplicates"
4. **Review results** in the tree view showing duplicate groups
5. **Select files** to keep or delete (click on files to toggle action)
6. **Delete selected files** by clicking "Delete Selected Files"

### UI Features

#### Main Interface
- **Folder Selection**: Choose the root folder to search for duplicates
- **Progress Tracking**: Real-time progress bar and detailed logs
- **Results Display**: Tree view showing duplicate groups and file details
- **Action Buttons**: Various options for selecting and managing duplicates

#### Duplicate Display
- Duplicates are displayed in a hierarchical tree with sections
- Each section groups all duplicates of a file together
- Users can click on files to toggle between "keep" and "delete" actions
- **Default mode is "keep"**: The first file in each group is set to "keep", others to "delete"
- File information includes name, size, and relative path

#### User Controls
- **Stop Search**: Cancel the search at any time to proceed with current results
- **Auto-Select**: Keep first file in each group, delete the rest
- **Select All to Keep/Delete**: Bulk selection options
- **Clear Results**: Reset the interface for a new search
- **Double-click files**: Open file location in system file manager

### File Actions
- **Safe Deletion**: Files are moved to system trash/recycle bin (not permanently deleted)
- **Confirmation Dialog**: Always asks for confirmation before deleting files
- **Error Handling**: Reports any files that couldn't be moved to trash

## Features

### Duplicate Detection Algorithm
1. **File size comparison**: First compare file sizes for optimization (if sizes don't match, files can't be identical)
2. **Hash calculation**: Use MD5 hash to detect identical content regardless of file type (text, binary, etc.)
3. **Grouping**: Files with identical hashes are considered duplicates and grouped together
4. **Recursive search**: Search recursively through all subfolders

### File Handling
- **Ignored files**: Hidden files (starting with '.') are ignored
- **Inaccessible files**: Files with insufficient permissions or currently in use are ignored
- **All file types**: Process all file types (text, binary, media, etc.)
- **Progress tracking**: Real-time updates on search progress
- **Cancellation**: Search can be stopped at any time

## Testing

### Generate Test Files
A test generator script is included to create sample duplicate files for testing:

```bash
# Create test structure
python3 test_generator.py

# View test structure summary
python3 test_generator.py --summary
```

This creates a `test_duplicates` folder with:
- Multiple duplicate files with same content
- Files with different names but same content
- Files in different subdirectories
- Unique files (no duplicates)
- Hidden files (should be ignored)
- Empty files
- Various file types: text, binary, code, data

### Testing the Application
1. Run the test generator: `python3 test_generator.py`
2. Launch the application: `python3 main.py`
3. Select the `test_duplicates` folder
4. Run the search and verify results

## Project Structure

```
duplication_deleter/
├── main.py                 # Application entry point
├── requirements.txt        # Python dependencies
├── test_generator.py       # Test file generator
├── README.md              # This file
└── src/                   # Source code
    ├── __init__.py
    ├── duplicate_detector.py  # Core duplicate detection logic
    ├── file_manager.py        # File operations and trash handling
    └── main_ui.py            # Main UI application
```

## Technical Specifications

- **Platform**: Cross-platform (Windows, macOS, Linux)
- **Language**: Python 3.7+
- **Hash Algorithm**: MD5
- **UI Framework**: TKinter (with platform-appropriate themes)
- **File Operations**: Move to Trash (using send2trash library)
- **Search**: Recursive through all subdirectories
- **Threading**: Non-blocking UI with background processing

## Troubleshooting

### Common Issues
1. **Permission errors**: Ensure the application has read access to the selected folder
2. **Files in use**: Some files may not be deletable if they're currently open in other applications
3. **Large folders**: Searching very large folders may take time; use the progress indicator and stop function as needed

### Performance Tips
- **Start with smaller folders** to test the application
- **Use the stop function** if searches take too long
- **Close other applications** that might be using files you want to delete

