"""
Main UI application for the Duplicate File Deleter.
Built with TKinter for cross-platform use.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import platform
import subprocess
from typing import Dict, List, Optional, Set
from datetime import datetime

from .duplicate_detector import DuplicateDetector
from .file_manager import FileManager


class DuplicateFileDeleterApp:
    """
    Main application class for the Duplicate File Deleter.
    """
    
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate File Deleter")
        self.root.geometry("1000x700")
        self.root.resizable(True, True)
        
        # Initialize components
        self.detector = DuplicateDetector(progress_callback=self.update_progress)
        self.file_manager = FileManager()
        
        # Application state
        self.selected_folder = tk.StringVar()
        self.is_searching = False
        self.search_thread = None
        self.duplicates = {}
        self.duplicate_groups = []
        self.file_selections = {}  # file_path -> boolean (True = selected for deletion)
        
        # Create UI
        self.create_widgets()
        
        # Style configuration
        self.configure_styles()
    
    def configure_styles(self):
        """Configure custom styles for the application."""
        style = ttk.Style()
        
        # Use appropriate theme based on platform
        system = platform.system()
        if system == "Darwin":  # macOS
            style.theme_use('aqua')
        elif system == "Windows":
            style.theme_use('vista')
        else:  # Linux and others
            style.theme_use('clam')
        
        # Configure custom styles
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'))
        style.configure('Header.TLabel', font=('Arial', 12, 'bold'))
        style.configure('Info.TLabel', font=('Arial', 10))
        style.configure('Success.TLabel', foreground='green')
        style.configure('Error.TLabel', foreground='red')
        style.configure('Warning.TLabel', foreground='orange')
    
    def create_widgets(self):
        """Create and arrange all UI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="Duplicate File Deleter", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # Folder selection section
        self.create_folder_selection_section(main_frame)
        
        # Progress section
        self.create_progress_section(main_frame)
        
        # Results section
        self.create_results_section(main_frame)
        
        # Action buttons
        self.create_action_buttons(main_frame)
        
        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(3, weight=1)
    
    def create_folder_selection_section(self, parent):
        """Create the folder selection section."""
        # Folder selection frame
        folder_frame = ttk.LabelFrame(parent, text="Select Folder to Search", padding="10")
        folder_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Folder path entry
        self.folder_entry = ttk.Entry(folder_frame, textvariable=self.selected_folder, width=60)
        self.folder_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Browse button
        self.browse_button = ttk.Button(folder_frame, text="Browse", command=self.browse_folder)
        self.browse_button.grid(row=0, column=1)
        
        # Search button
        self.search_button = ttk.Button(folder_frame, text="Search for Duplicates", command=self.start_search)
        self.search_button.grid(row=0, column=2, padx=(10, 0))
        
        # Stop button
        self.stop_button = ttk.Button(folder_frame, text="Stop Search", command=self.stop_search, state=tk.DISABLED)
        self.stop_button.grid(row=0, column=3, padx=(10, 0))
        
        folder_frame.columnconfigure(0, weight=1)
    
    def create_progress_section(self, parent):
        """Create the progress section."""
        # Progress frame
        progress_frame = ttk.LabelFrame(parent, text="Search Progress", padding="10")
        progress_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Progress bar
        self.progress_bar = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        # Progress label
        self.progress_label = ttk.Label(progress_frame, text="Ready to search", style='Info.TLabel')
        self.progress_label.grid(row=0, column=1)
        
        # Progress text area
        self.progress_text = scrolledtext.ScrolledText(progress_frame, height=4, width=80)
        self.progress_text.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(10, 0))
        
        progress_frame.columnconfigure(0, weight=1)
    
    def create_results_section(self, parent):
        """Create the results section."""
        # Results frame
        results_frame = ttk.LabelFrame(parent, text="Duplicate Files", padding="10")
        results_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        
        # Create treeview for displaying duplicates
        self.tree = ttk.Treeview(results_frame, columns=('Delete', 'Size', 'Path', 'file_path'), show='tree headings')
        self.tree.heading('#0', text='File Name')
        self.tree.heading('Delete', text='Delete')
        self.tree.heading('Size', text='Size')
        self.tree.heading('Path', text='Path')
        
        # Configure column widths
        self.tree.column('#0', width=300)
        self.tree.column('Delete', width=60)
        self.tree.column('Size', width=100)
        self.tree.column('Path', width=400)
        self.tree.column('file_path', width=0)  # Hidden column for storing file path
        
        # Scrollbars for treeview
        tree_scrollbar_y = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scrollbar_x = ttk.Scrollbar(results_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scrollbar_y.set, xscrollcommand=tree_scrollbar_x.set)
        
        # Grid treeview and scrollbars
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        tree_scrollbar_y.grid(row=0, column=1, sticky=(tk.N, tk.S))
        tree_scrollbar_x.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Results info
        self.results_info = ttk.Label(results_frame, text="No duplicates found yet", style='Info.TLabel')
        self.results_info.grid(row=2, column=0, columnspan=2, pady=(10, 0))
        
        # Bind events
        self.tree.bind('<Double-1>', self.on_item_double_click)
        self.tree.bind('<Button-1>', self.on_item_click)
        
        results_frame.columnconfigure(0, weight=1)
        results_frame.rowconfigure(0, weight=1)
    
    def create_action_buttons(self, parent):
        """Create the action buttons section."""
        # Action frame
        action_frame = ttk.Frame(parent)
        action_frame.grid(row=4, column=0, columnspan=3, pady=(10, 0))
        
        # Select all button
        self.select_all_button = ttk.Button(action_frame, text="Select All", 
                                           command=self.select_all, state=tk.DISABLED)
        self.select_all_button.grid(row=0, column=0, padx=(0, 10))
        
        # Deselect all button
        self.deselect_all_button = ttk.Button(action_frame, text="Deselect All", 
                                             command=self.deselect_all, state=tk.DISABLED)
        self.deselect_all_button.grid(row=0, column=1, padx=(0, 10))
        
        # Auto-select button (select all except first in each group)
        self.auto_select_button = ttk.Button(action_frame, text="Auto-Select (Keep First)", 
                                            command=self.auto_select, state=tk.DISABLED)
        self.auto_select_button.grid(row=0, column=2, padx=(0, 10))
        
        # Delete selected button
        self.delete_button = ttk.Button(action_frame, text="Delete Selected Files", 
                                       command=self.delete_selected, state=tk.DISABLED)
        self.delete_button.grid(row=0, column=3, padx=(0, 10))
        
        # Clear results button
        self.clear_button = ttk.Button(action_frame, text="Clear Results", 
                                      command=self.clear_results, state=tk.DISABLED)
        self.clear_button.grid(row=0, column=4)
    
    def browse_folder(self):
        """Open folder selection dialog."""
        folder_path = filedialog.askdirectory(title="Select folder to search for duplicates")
        if folder_path:
            self.selected_folder.set(folder_path)
    
    def start_search(self):
        """Start the duplicate search process."""
        folder_path = self.selected_folder.get().strip()
        if not folder_path:
            messagebox.showerror("Error", "Please select a folder to search.")
            return
        
        if not os.path.exists(folder_path):
            messagebox.showerror("Error", "Selected folder does not exist.")
            return
        
        # Clear previous results
        self.clear_results()
        
        # Update UI state
        self.is_searching = True
        self.search_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.browse_button.config(state=tk.DISABLED)
        
        # Start search in separate thread
        self.search_thread = threading.Thread(target=self.search_duplicates, args=(folder_path,))
        self.search_thread.daemon = True
        self.search_thread.start()
    
    def stop_search(self):
        """Stop the current search."""
        if self.detector:
            self.detector.stop()
        self.is_searching = False
        self.update_progress(0, "Search stopped by user")
        self.reset_ui_state()
    
    def search_duplicates(self, folder_path: str):
        """Search for duplicates in the specified folder."""
        try:
            self.duplicates = self.detector.find_duplicates(folder_path)
            
            # Update UI on main thread
            self.root.after(0, self.display_results)
            
        except Exception as e:
            error_msg = f"Error during search: {str(e)}"
            self.root.after(0, lambda: self.update_progress(0, error_msg))
            self.root.after(0, lambda: messagebox.showerror("Search Error", error_msg))
        finally:
            self.root.after(0, self.reset_ui_state)
    
    def display_results(self):
        """Display the search results in the treeview."""
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.file_selections.clear()
        self.duplicate_groups.clear()
        
        if not self.duplicates:
            self.results_info.config(text="No duplicates found")
            return
        
        total_files = 0
        group_count = 0
        
        for hash_value, files in self.duplicates.items():
            group_count += 1
            total_files += len(files)
            
            # Create group header
            group_name = f"Group {group_count} ({len(files)} files)"
            group_item = self.tree.insert('', 'end', text=group_name, values=('', '', '', ''))
            
            # Add files to group
            for i, file_path in enumerate(files):
                file_info = self.file_manager.get_file_info(file_path)
                if file_info:
                    relative_path = self.file_manager.get_relative_path(file_path, self.selected_folder.get())
                    size_str = self.file_manager.format_file_size(file_info['size'])
                    
                    # Default selection: nothing is selected initially
                    is_selected = False
                    self.file_selections[file_path] = is_selected
                    
                    # Insert file item with checkbox in Delete column
                    checkbox_text = "☑" if is_selected else "☐"
                    file_item = self.tree.insert(group_item, 'end', text=file_info['name'], 
                                               values=(checkbox_text, size_str, relative_path, file_path))
                    
                    # Store file path in item for easy access
                    self.tree.set(file_item, 'file_path', file_path)
            
            # Store group information
            self.duplicate_groups.append({
                'hash': hash_value,
                'files': files,
                'tree_item': group_item
            })
        
        # Expand all groups
        for item in self.tree.get_children():
            self.tree.item(item, open=True)
        
        # Update results info
        self.results_info.config(text=f"Found {group_count} duplicate groups with {total_files} files")
        
        # Enable action buttons
        self.select_all_button.config(state=tk.NORMAL)
        self.deselect_all_button.config(state=tk.NORMAL)
        self.auto_select_button.config(state=tk.NORMAL)
        self.delete_button.config(state=tk.NORMAL)
        self.clear_button.config(state=tk.NORMAL)
    
    def on_item_click(self, event):
        """Handle item click to toggle checkbox."""
        # Get the item that was clicked
        item = self.tree.identify_row(event.y)
        if not item:
            return
        
        # Get the column that was clicked
        column = self.tree.identify_column(event.x)
        
        # Check if it's a file item (has file_path)
        try:
            file_path = self.tree.set(item, 'file_path')
            if file_path and file_path in self.file_selections:
                # Toggle checkbox (works for any column click on file)
                current_selection = self.file_selections[file_path]
                new_selection = not current_selection
                self.file_selections[file_path] = new_selection
                
                # Update display
                self.update_file_display(item, file_path, new_selection)
                self.update_group_display_for_file(item)
                
            # Check if it's a group item (no file_path)
            elif not file_path:
                # Handle group selection
                self.toggle_group_selection(item)
        except tk.TclError:
            pass  # Not a valid item
    
    def update_file_display(self, item, file_path, is_selected):
        """Update the display of a file item with checkbox."""
        # Update checkbox in Delete column
        checkbox_text = "☑" if is_selected else "☐"
        self.tree.set(item, 'Delete', checkbox_text)
    
    def update_group_display_for_file(self, file_item):
        """Update group display when a file selection changes."""
        # Find the parent group
        parent = self.tree.parent(file_item)
        if parent:
            self.update_group_display(parent)
    
    def toggle_group_selection(self, group_item):
        """Toggle selection for all files in a group (except first one)."""
        children = self.tree.get_children(group_item)
        if not children:
            return
        
        # Check current state of group - if any file is selected, deselect all
        # If none are selected, select all except first
        any_selected = False
        for child in children:
            try:
                file_path = self.tree.set(child, 'file_path')
                if file_path in self.file_selections and self.file_selections[file_path]:
                    any_selected = True
                    break
            except tk.TclError:
                continue
        
        # Toggle group selection
        for i, child in enumerate(children):
            try:
                file_path = self.tree.set(child, 'file_path')
                if file_path in self.file_selections:
                    if any_selected:
                        # Deselect all
                        self.file_selections[file_path] = False
                    else:
                        # Select all except first
                        self.file_selections[file_path] = i > 0
                    
                    self.update_file_display(child, file_path, self.file_selections[file_path])
            except tk.TclError:
                continue
        
        # Update group checkbox
        self.update_group_display(group_item)
    
    def update_group_display(self, group_item):
        """Update the display of a group item with checkbox."""
        children = self.tree.get_children(group_item)
        if not children:
            return
        
        # Check if any files are selected
        any_selected = False
        for child in children:
            try:
                file_path = self.tree.set(child, 'file_path')
                if file_path in self.file_selections and self.file_selections[file_path]:
                    any_selected = True
                    break
            except tk.TclError:
                continue
        
        # Update group checkbox in Delete column
        checkbox_text = "☑" if any_selected else "☐"
        self.tree.set(group_item, 'Delete', checkbox_text)
    
    def on_item_double_click(self, event):
        """Handle item double-click to open file location."""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return
        
        try:
            file_path = self.tree.set(item, 'file_path')
            if file_path and os.path.exists(file_path):
                # Open file location in system file manager
                system = platform.system()
                if system == "Darwin":  # macOS
                    subprocess.run(["open", "-R", file_path])
                elif system == "Windows":
                    subprocess.run(["explorer", "/select,", file_path])
                else:  # Linux and others
                    subprocess.run(["xdg-open", os.path.dirname(file_path)])
        except (tk.TclError, subprocess.SubprocessError):
            pass
    
    def select_all(self):
        """Select all files for deletion."""
        for file_path in self.file_selections:
            self.file_selections[file_path] = True
        self.refresh_tree_display()
    
    def deselect_all(self):
        """Deselect all files."""
        for file_path in self.file_selections:
            self.file_selections[file_path] = False
        self.refresh_tree_display()
    
    def auto_select(self):
        """Auto-select: select all files except the first one in each group."""
        for group in self.duplicate_groups:
            files = group['files']
            for i, file_path in enumerate(files):
                self.file_selections[file_path] = i > 0  # True for all except first
        self.refresh_tree_display()
    
    def refresh_tree_display(self):
        """Refresh the checkbox display in the tree view."""
        for group_item in self.tree.get_children():
            for child in self.tree.get_children(group_item):
                try:
                    file_path = self.tree.set(child, 'file_path')
                    if file_path in self.file_selections:
                        self.update_file_display(child, file_path, self.file_selections[file_path])
                except tk.TclError:
                    pass
            
            # Update group display
            self.update_group_display(group_item)
    
    def delete_selected(self):
        """Delete selected files after confirmation."""
        files_to_delete = [path for path, is_selected in self.file_selections.items() if is_selected]
        
        if not files_to_delete:
            messagebox.showinfo("No Files Selected", "No files are selected for deletion.")
            return
        
        # Show confirmation dialog
        message = f"Are you sure you want to move {len(files_to_delete)} files to the trash?\n\nThis action cannot be undone."
        if not messagebox.askyesno("Confirm Deletion", message):
            return
        
        # Delete files
        self.file_manager.clear_errors()
        results = self.file_manager.move_files_to_trash(files_to_delete)
        
        # Show results
        success_count = sum(1 for success in results.values() if success)
        error_count = len(results) - success_count
        
        if error_count == 0:
            messagebox.showinfo("Success", f"Successfully moved {success_count} files to trash.")
        else:
            error_msg = f"Moved {success_count} files to trash.\n{error_count} files could not be deleted.\n\nErrors:\n"
            error_msg += "\n".join(self.file_manager.get_errors()[:5])  # Show first 5 errors
            messagebox.showwarning("Partial Success", error_msg)
        
        # Remove deleted files from display
        self.remove_deleted_files_from_display(files_to_delete)
    
    def remove_deleted_files_from_display(self, deleted_files: List[str]):
        """Remove deleted files from the tree display."""
        for group_item in self.tree.get_children():
            children_to_remove = []
            for child in self.tree.get_children(group_item):
                try:
                    file_path = self.tree.set(child, 'file_path')
                    if file_path in deleted_files:
                        children_to_remove.append(child)
                except tk.TclError:
                    pass
            
            # Remove children
            for child in children_to_remove:
                self.tree.delete(child)
                
            # Remove group if no children left
            if not self.tree.get_children(group_item):
                self.tree.delete(group_item)
            else:
                # Update group display after removing files
                self.update_group_display(group_item)
        
        # Update file selections
        for file_path in deleted_files:
            self.file_selections.pop(file_path, None)
    
    def clear_results(self):
        """Clear all results and reset the UI."""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.duplicates.clear()
        self.duplicate_groups.clear()
        self.file_selections.clear()
        
        self.results_info.config(text="No duplicates found yet")
        self.progress_bar['value'] = 0
        self.progress_label.config(text="Ready to search")
        self.progress_text.delete(1.0, tk.END)
        
        # Disable action buttons
        self.select_all_button.config(state=tk.DISABLED)
        self.deselect_all_button.config(state=tk.DISABLED)
        self.auto_select_button.config(state=tk.DISABLED)
        self.delete_button.config(state=tk.DISABLED)
        self.clear_button.config(state=tk.DISABLED)
    
    def update_progress(self, progress: float, message: str):
        """Update the progress bar and message."""
        self.progress_bar['value'] = progress
        self.progress_label.config(text=f"{progress:.1f}%")
        
        # Add message to progress text
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.progress_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.progress_text.see(tk.END)
        
        # Update display
        self.root.update_idletasks()
    
    def reset_ui_state(self):
        """Reset UI state after search completion."""
        self.is_searching = False
        self.search_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.browse_button.config(state=tk.NORMAL)


def main():
    """Main entry point for the application."""
    root = tk.Tk()
    app = DuplicateFileDeleterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main() 