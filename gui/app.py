import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
import threading
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from cli.commands import find_duplicates
from dedupe.indexer import build_index, load_image
from dedupe.comparer import deep_similarity

class DuplicateFinderGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Duplicate Image Finder")
        self.root.geometry("1000x700")
        
        self.duplicate_groups = []
        self.scanning = False
        
        self.setup_ui()
        
    def setup_ui(self):
        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill=tk.X)
        
        ttk.Label(top_frame, text="Directory:").pack(side=tk.LEFT)
        
        self.dir_var = tk.StringVar()
        self.dir_entry = ttk.Entry(top_frame, textvariable=self.dir_var, width=50)
        self.dir_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        self.browse_btn = ttk.Button(top_frame, text="Browse", command=self.browse_directory)
        self.browse_btn.pack(side=tk.LEFT)
        
        params_frame = ttk.LabelFrame(self.root, text="Parameters", padding="10")
        params_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(params_frame, text="Similarity Threshold (%):").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.threshold_var = tk.IntVar(value=95)
        threshold_slider = ttk.Scale(params_frame, from_=50, to=100, variable=self.threshold_var, orient=tk.HORIZONTAL)
        threshold_slider.grid(row=0, column=1, sticky=tk.EW, padx=5)
        self.threshold_label = ttk.Label(params_frame, text="95")
        self.threshold_label.grid(row=0, column=2)
        threshold_slider.config(command=lambda v: self.threshold_label.config(text=f"{int(float(v))}"))
        
        ttk.Label(params_frame, text="Hash Distance:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.hash_dist_var = tk.IntVar(value=5)
        hash_dist_spinner = ttk.Spinbox(params_frame, from_=0, to=64, textvariable=self.hash_dist_var, width=10)
        hash_dist_spinner.grid(row=1, column=1, sticky=tk.W, padx=5)
        ttk.Label(params_frame, text="(lower = stricter)").grid(row=1, column=2, sticky=tk.W)
        
        ttk.Label(params_frame, text="Pixel Tolerance:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.tolerance_var = tk.IntVar(value=10)
        tolerance_spinner = ttk.Spinbox(params_frame, from_=0, to=255, textvariable=self.tolerance_var, width=10)
        tolerance_spinner.grid(row=2, column=1, sticky=tk.W, padx=5)
        ttk.Label(params_frame, text="(lower = stricter)").grid(row=2, column=2, sticky=tk.W)
        
        ttk.Label(params_frame, text="Comparison Size:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.size_var = tk.IntVar(value=64)
        size_spinner = ttk.Spinbox(params_frame, from_=8, to=512, textvariable=self.size_var, width=10)
        size_spinner.grid(row=3, column=1, sticky=tk.W, padx=5)
        ttk.Label(params_frame, text="(NxN pixels)").grid(row=3, column=2, sticky=tk.W)
        
        params_frame.columnconfigure(1, weight=1)
        
        action_frame = ttk.Frame(self.root, padding="10")
        action_frame.pack(fill=tk.X)
        
        self.scan_btn = ttk.Button(action_frame, text="Scan for Duplicates", command=self.start_scan)
        self.scan_btn.pack(side=tk.LEFT)
        
        self.stop_btn = ttk.Button(action_frame, text="Stop", command=self.stop_scan, state=tk.DISABLED)
        self.stop_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_btn = ttk.Button(action_frame, text="Clear Results", command=self.clear_results)
        self.clear_btn.pack(side=tk.LEFT)
        
        progress_frame = ttk.Frame(self.root, padding="10")
        progress_frame.pack(fill=tk.X)
        
        self.progress_var = tk.StringVar(value="Ready")
        self.progress_label = ttk.Label(progress_frame, textvariable=self.progress_var)
        self.progress_label.pack(side=tk.LEFT)
        
        self.progress_bar = ttk.Progressbar(progress_frame, mode='indeterminate')
        self.progress_bar.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)
        
        results_frame = ttk.LabelFrame(self.root, text="Duplicate Groups", padding="5")
        results_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        canvas = tk.Canvas(results_frame)
        scrollbar = ttk.Scrollbar(results_frame, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)
        
        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.results_container = self.scrollable_frame
        
    def browse_directory(self):
        directory = filedialog.askdirectory(title="Select Directory to Scan")
        if directory:
            self.dir_var.set(directory)
    
    def start_scan(self):
        directory = self.dir_var.get()
        if not directory or not Path(directory).exists():
            messagebox.showerror("Error", "Please select a valid directory")
            return
        
        self.scanning = True
        self.scan_btn.config(state=tk.DISABLED)
        self.stop_btn.config(state=tk.NORMAL)
        self.browse_btn.config(state=tk.DISABLED)
        self.clear_results()
        
        self.progress_var.set("Scanning...")
        self.progress_bar.start()
        
        thread = threading.Thread(target=self.run_scan, daemon=True)
        thread.start()
    
    def stop_scan(self):
        self.scanning = False
        self.progress_var.set("Scan stopped")
        self.progress_bar.stop()
        self.scan_btn.config(state=tk.NORMAL)
        self.stop_btn.config(state=tk.DISABLED)
        self.browse_btn.config(state=tk.NORMAL)
    
    def run_scan(self):
        try:
            directory = self.dir_var.get()
            threshold = self.threshold_var.get()
            hash_distance = self.hash_dist_var.get()
            size = self.size_var.get()
            tolerance = self.tolerance_var.get()
            
            self.root.after(0, lambda: self.progress_var.set("Building index..."))
            
            index, tree, records = build_index(directory, verbose=False)
            
            if len(records) == 0:
                self.root.after(0, lambda: messagebox.showinfo("Info", "No images found in directory"))
                self.root.after(0, self.stop_scan)
                return
            
            self.root.after(0, lambda: self.progress_var.set(f"Comparing {len(records)} images..."))
            
            duplicate_groups = []
            processed = set()
            comparison_size = (size, size)
            
            for i, record in enumerate(records):
                if not self.scanning:
                    break
                    
                if record.path in processed:
                    continue
                
                progress_text = f"Processing {i + 1}/{len(records)} images..."
                self.root.after(0, lambda t=progress_text: self.progress_var.set(t))
                
                candidates = tree.search(record.hash, threshold=hash_distance)
                
                img1 = load_image(record.path)
                if img1 is None:
                    continue
                
                group = []
                
                for candidate in candidates:
                    if not self.scanning:
                        break
                        
                    if candidate.path == record.path or candidate.path in processed:
                        continue
                    
                    img2 = load_image(candidate.path)
                    if img2 is None:
                        continue
                    
                    similarity = deep_similarity(img1, img2, size=comparison_size, tolerance=tolerance)
                    img2.close()
                    
                    if similarity >= threshold:
                        if not group:
                            group.append((record.path, 100.0))
                        group.append((candidate.path, similarity))
                        processed.add(candidate.path)
                
                img1.close()
                
                if group:
                    processed.add(record.path)
                    duplicate_groups.append(group)
            
            self.duplicate_groups = duplicate_groups
            
            self.root.after(0, self.display_results)
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", f"Scan failed: {str(e)}"))
        finally:
            self.root.after(0, self.stop_scan)
    
    def display_results(self):
        for widget in self.results_container.winfo_children():
            widget.destroy()
        
        if not self.duplicate_groups:
            ttk.Label(self.results_container, text="No duplicates found!", 
                     font=('Arial', 12)).pack(pady=20)
            self.progress_var.set("No duplicates found")
            return
        
        self.progress_var.set(f"Found {len(self.duplicate_groups)} duplicate group(s)")
        
        for idx, group in enumerate(self.duplicate_groups, 1):
            group_frame = ttk.LabelFrame(self.results_container, 
                                         text=f"Group {idx} ({len(group)} images)",
                                         padding="10")
            group_frame.pack(fill=tk.X, pady=5, padx=5)
            
            for img_path, similarity in group:
                self.create_image_row(group_frame, img_path, similarity, idx)
    
    def create_image_row(self, parent, img_path, similarity, group_id):
        row_frame = ttk.Frame(parent)
        row_frame.pack(fill=tk.X, pady=2)
        
        try:
            img = Image.open(img_path)
            img.thumbnail((80, 80))
            photo = ImageTk.PhotoImage(img)
            
            thumb_label = ttk.Label(row_frame, image=photo)
            thumb_label.image = photo  # Keep reference
            thumb_label.pack(side=tk.LEFT, padx=5)
        except:
            ttk.Label(row_frame, text="[No Preview]", width=10).pack(side=tk.LEFT, padx=5)
        
        info_frame = ttk.Frame(row_frame)
        info_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        path_label = ttk.Label(info_frame, text=str(img_path), foreground="blue", cursor="hand2")
        path_label.pack(anchor=tk.W)
        path_label.bind("<Button-1>", lambda e: self.open_file_location(img_path))
        
        similarity_text = f"Similarity: {similarity:.2f}%"
        if similarity == 100.0:
            similarity_text += " (Reference)"
        ttk.Label(info_frame, text=similarity_text, foreground="green" if similarity >= 98 else "orange").pack(anchor=tk.W)
        
        btn_frame = ttk.Frame(row_frame)
        btn_frame.pack(side=tk.RIGHT)
        
        ttk.Button(btn_frame, text="Open", command=lambda: self.open_image(img_path), width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Delete", command=lambda: self.delete_image(img_path, group_id), width=8).pack(side=tk.LEFT, padx=2)
    
    def open_image(self, path):
        import subprocess
        import platform
        
        try:
            if platform.system() == 'Darwin':
                subprocess.call(['open', path])
            elif platform.system() == 'Windows':
                subprocess.call(['start', path], shell=True)
            else:
                subprocess.call(['xdg-open', path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open image: {str(e)}")
    
    def open_file_location(self, path):
        import subprocess
        import platform
        
        try:
            folder = str(Path(path).parent)
            if platform.system() == 'Darwin':
                subprocess.call(['open', folder])
            elif platform.system() == 'Windows':
                subprocess.call(['explorer', folder])
            else:
                subprocess.call(['xdg-open', folder])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open location: {str(e)}")
    
    def delete_image(self, path, group_id):
        result = messagebox.askyesno("Confirm Delete", 
                                     f"Are you sure you want to delete this file?\n\n{path}")
        if result:
            try:
                Path(path).unlink()
                messagebox.showinfo("Success", "File deleted successfully")
                # Refresh results
                self.display_results()
            except Exception as e:
                messagebox.showerror("Error", f"Could not delete file: {str(e)}")
    
    def clear_results(self):
        for widget in self.results_container.winfo_children():
            widget.destroy()
        self.duplicate_groups = []
        self.progress_var.set("Ready")

def main():
    root = tk.Tk()
    app = DuplicateFinderGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
