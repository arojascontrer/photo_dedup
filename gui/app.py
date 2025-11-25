import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent))

from main import find_duplicates_for_gui

class DuplicateFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate Image Finder")
        self.root.geometry("900x700")
        
        self.duplicate_groups = []

        self.setup_ui()
        
    def setup_ui(self):
        # Top Frame - Directory Selection
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Directory:").pack(side=tk.LEFT)
        
        self.dir_var = tk.StringVar()
        self.dir_entry = ttk.Entry(top_frame, textvariable=self.dir_var, width=50)
        self.dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        ttk.Button(top_frame, text="Browse", command=self.browse_directory).pack(side=tk.LEFT)
        
        # Action Frame
        action_frame = ttk.Frame(self.root, padding="10")
        action_frame.pack(fill=tk.X)
        
        ttk.Button(action_frame, text="Scan for Duplicates", command=self.start_scan).pack(side=tk.LEFT)
        
        # Status Label
        self.status_var = tk.StringVar(value="Ready - Select a directory to scan")
        ttk.Label(self.root, textvariable=self.status_var, padding="10").pack()
        
    def browse_directory(self):
        directory = filedialog.askdirectory(title="Select Directory to Scan")
        if directory:
            self.dir_var.set(directory)
            self.status_var.set(f"Selected: {directory}")
    
    def start_scan(self):
        directory = self.dir_var.get()
        if not directory:
            self.status_var.set("Error: Please select a directory first")
            return
        
        if not Path(directory).exists():
            self.status_var.set("Error: Directory does not exist")
            return
        
        self.status_var.set(f"Ready to scan: {directory}")
        # Scanning logic will be added here

def main():
    root = tk.Tk()
    app = DuplicateFinderGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

