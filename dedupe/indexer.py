import os
from pathlib import Path
from PIL import Image
from .hashers import tiny_hash
from .structures import HashTable, BKTree

VALID_EXT = (".jpg", ".jpeg", ".png", ".bmp", ".webp")


class ImageRecord:
    def __init__(self, path, hash_value):
        self.path = path
        self.hash = hash_value

    def __repr__(self):
        return f"ImageRecord(path={self.path}, hash={self.hash})"


def load_image(path):
    try:
        return Image.open(path)
    except (IOError, OSError) as e:
        return None


def scan_folder(folder_path):
    folder = Path(folder_path)
    if not folder.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")
    if not folder.is_dir():
        raise NotADirectoryError(f"Not a directory: {folder_path}")
    
    entries = []

    for name in os.listdir(folder_path):
        if name.lower().endswith(VALID_EXT):
            full = os.path.join(folder_path, name)
            entries.append((name, full))
    return entries


def build_index(folder_path, verbose = False):
    index = HashTable(size=2048)
    records = []
    tree = BKTree()
    files = scan_folder(folder_path)

    if verbose:
        print(f"Found {len(files)} image files")

    for i, (filename, path) in enumerate(files, 1):
        img = load_image(path)
        if img is None:
            if verbose:
                print(f"  Skipped (load failed): {filename}")
            continue
        
        h = tiny_hash(img)
        img.close()
        record = ImageRecord(path, h)
        index.insert(h, record)
        tree.add(h, record)
        records.append(record)
        
        if verbose and i % 100 == 0:
            print(f"  Processed {i}/{len(files)} files...")
    
    if verbose:
        print(f"Successfully indexed {len(records)} images")
    
    return index, tree, records
